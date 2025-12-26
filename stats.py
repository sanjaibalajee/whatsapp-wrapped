# stats - all the number crunching

import re
import math
from datetime import timedelta
from collections import Counter, defaultdict

from constants import CHAT_STOP_WORDS, TOPIC_ONLY_STOP_WORDS
from parser import extract_emojis


def format_duration(seconds):
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"


def get_basic_stats(df):
    user_df = df[~df['is_system']]

    if user_df.empty:
        return None

    date_range = (user_df['date'].max() - user_df['date'].min()).days

    return {
        "total_messages": len(user_df),
        "total_participants": user_df['sender'].nunique(),
        "date_range_days": date_range,
        "first_message": user_df['datetime'].min(),
        "last_message": user_df['datetime'].max(),
        "total_words": user_df['word_count'].sum(),
        "total_characters": user_df['char_count'].sum(),
    }


def get_top_chatters(df, top_n=10):
    user_df = df[~df['is_system']]
    counts = user_df['sender'].value_counts().head(top_n)
    return counts.to_dict()


def get_hourly_activity(df):
    user_df = df[~df['is_system']]
    return user_df['hour'].value_counts().sort_index().to_dict()


def get_daily_activity(df):
    user_df = df[~df['is_system']]
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    counts = user_df['day_of_week'].value_counts()
    return {day: counts.get(day, 0) for day in day_order}


def get_emoji_stats(df, top_n=15):
    user_df = df[~df['is_system']]
    all_emojis = []

    for msg in user_df['message']:
        all_emojis.extend(extract_emojis(str(msg)))

    return dict(Counter(all_emojis).most_common(top_n))


def get_emoji_stats_by_user(df, top_n=5):
    user_df = df[~df['is_system']]
    user_emojis = {}

    for sender in user_df['sender'].unique():
        sender_msgs = user_df[user_df['sender'] == sender]['message']
        emojis = []
        for msg in sender_msgs:
            emojis.extend(extract_emojis(str(msg)))

        if emojis:
            user_emojis[sender] = {
                "total": len(emojis),
                "top": dict(Counter(emojis).most_common(3))
            }

    return dict(sorted(user_emojis.items(), key=lambda x: x[1]['total'], reverse=True)[:top_n])


def get_media_stats(df):
    user_df = df[~df['is_system']]
    media_df = user_df[user_df['media_type'].notna()]

    if media_df.empty:
        return {"total": 0}

    by_type = media_df['media_type'].value_counts().to_dict()
    by_user = media_df['sender'].value_counts().head(5).to_dict()

    return {
        "total": len(media_df),
        "by_type": by_type,
        "top_sharers": by_user
    }


def get_word_stats(df, top_n=20):
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    # filter out participant names
    name_parts = set()
    for sender in user_df['sender'].unique():
        for part in sender.lower().split():
            if len(part) > 2:
                name_parts.add(part)

    words = []
    for msg in user_df['message']:
        clean_msg = re.sub(r'<[^>]+>', '', str(msg))  # rm system annotations
        clean_msg = re.sub(r'@\S+', '', clean_msg)  # rm mentions

        msg_words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_msg.lower())
        words.extend([w for w in msg_words if w not in CHAT_STOP_WORDS and w not in name_parts])

    return dict(Counter(words).most_common(top_n))


def get_conversation_starters(df, gap_minutes=60):
    user_df = df[~df['is_system']].sort_values('datetime')

    if len(user_df) < 2:
        return {}

    starters = Counter()
    prev_time = None

    for _, row in user_df.iterrows():
        if prev_time is None:
            starters[row['sender']] += 1
        elif (row['datetime'] - prev_time) > timedelta(minutes=gap_minutes):
            starters[row['sender']] += 1
        prev_time = row['datetime']

    return dict(starters.most_common(10))


def get_night_owls(df):
    # 12am-5am crew
    user_df = df[~df['is_system']]
    night_df = user_df[(user_df['hour'] >= 0) & (user_df['hour'] < 5)]

    if night_df.empty:
        return {}

    return night_df['sender'].value_counts().head(5).to_dict()


def get_early_birds(df):
    # 5am-8am gang
    user_df = df[~df['is_system']]
    morning_df = user_df[(user_df['hour'] >= 5) & (user_df['hour'] < 8)]

    if morning_df.empty:
        return {}

    return morning_df['sender'].value_counts().head(5).to_dict()


def get_longest_messages(df, top_n=5):
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    avg_length = user_df.groupby('sender')['char_count'].mean()
    return avg_length.nlargest(top_n).to_dict()


def get_busiest_dates(df, top_n=5):
    user_df = df[~df['is_system']]
    return user_df['date'].value_counts().head(top_n).to_dict()


def get_response_pairs(df, window_minutes=5):
    # who replies to whom
    user_df = df[~df['is_system']].sort_values('datetime')

    if len(user_df) < 2:
        return {}

    pairs = Counter()
    prev_sender = None
    prev_time = None

    for _, row in user_df.iterrows():
        if prev_sender and prev_sender != row['sender']:
            if prev_time and (row['datetime'] - prev_time) <= timedelta(minutes=window_minutes):
                pairs[(prev_sender, row['sender'])] += 1
        prev_sender = row['sender']
        prev_time = row['datetime']

    return dict(pairs.most_common(10))


def get_double_texters(df):
    # msgs in a row before reply
    user_df = df[~df['is_system']].sort_values('datetime')

    if len(user_df) < 2:
        return {}

    double_texts = Counter()
    streak = 1
    prev_sender = None

    for _, row in user_df.iterrows():
        if row['sender'] == prev_sender:
            streak += 1
        else:
            if streak >= 2 and prev_sender:
                double_texts[prev_sender] += streak - 1
            streak = 1
        prev_sender = row['sender']

    if streak >= 2 and prev_sender:
        double_texts[prev_sender] += streak - 1

    return dict(double_texts.most_common(10))


def get_conversation_killers(df, silence_minutes=30):
    # whose msgs end convos
    user_df = df[~df['is_system']].sort_values('datetime').reset_index(drop=True)

    if len(user_df) < 2:
        return {}

    killers = Counter()
    total_msgs = Counter()

    for i in range(len(user_df) - 1):
        current = user_df.iloc[i]
        next_msg = user_df.iloc[i + 1]
        total_msgs[current['sender']] += 1

        time_gap = (next_msg['datetime'] - current['datetime']).total_seconds() / 60
        if time_gap > silence_minutes:
            killers[current['sender']] += 1

    kill_rates = {}
    for sender, kills in killers.items():
        if total_msgs[sender] > 10:
            kill_rates[sender] = {
                "kills": kills,
                "total": total_msgs[sender],
                "rate": round(kills / total_msgs[sender] * 100, 1)
            }

    return dict(sorted(kill_rates.items(), key=lambda x: x[1]['kills'], reverse=True)[:5])


def get_response_times(df):
    user_df = df[~df['is_system']].sort_values('datetime').reset_index(drop=True)

    if len(user_df) < 2:
        return {}

    response_times = defaultdict(list)

    for i in range(1, len(user_df)):
        current = user_df.iloc[i]
        prev = user_df.iloc[i - 1]

        if current['sender'] != prev['sender']:
            gap_seconds = (current['datetime'] - prev['datetime']).total_seconds()
            # only count <1hr responses
            if 0 < gap_seconds < 3600:
                response_times[current['sender']].append(gap_seconds)

    avg_times = {}
    for sender, times in response_times.items():
        if len(times) >= 5:
            avg_seconds = sum(times) / len(times)
            avg_times[sender] = {
                "avg_seconds": round(avg_seconds, 1),
                "avg_formatted": format_duration(avg_seconds),
                "response_count": len(times)
            }

    return dict(sorted(avg_times.items(), key=lambda x: x[1]['avg_seconds'])[:10])


def get_caps_users(df):
    # WHO TYPES LIKE THIS
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    caps_count = Counter()
    total_count = Counter()

    for _, row in user_df.iterrows():
        msg = row['message']
        letters = re.findall(r'[a-zA-Z]', msg)
        if len(letters) >= 5:
            total_count[row['sender']] += 1
            caps_letters = re.findall(r'[A-Z]', msg)
            if len(caps_letters) / len(letters) > 0.7:
                caps_count[row['sender']] += 1

    caps_rates = {}
    for sender, caps in caps_count.items():
        if total_count[sender] > 10:
            caps_rates[sender] = {
                "caps_messages": caps,
                "rate": round(caps / total_count[sender] * 100, 1)
            }

    return dict(sorted(caps_rates.items(), key=lambda x: x[1]['caps_messages'], reverse=True)[:5])


def get_question_askers(df):
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    questions = Counter()
    total = Counter()

    for _, row in user_df.iterrows():
        total[row['sender']] += 1
        if '?' in row['message']:
            questions[row['sender']] += 1

    question_stats = {}
    for sender, q_count in questions.items():
        if total[sender] > 10:
            question_stats[sender] = {
                "questions": q_count,
                "rate": round(q_count / total[sender] * 100, 1)
            }

    return dict(sorted(question_stats.items(), key=lambda x: x[1]['questions'], reverse=True)[:5])


def get_link_sharers(df):
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    url_pattern = r'https?://\S+'
    link_count = Counter()

    for _, row in user_df.iterrows():
        links = re.findall(url_pattern, row['message'])
        if links:
            link_count[row['sender']] += len(links)

    return dict(link_count.most_common(5))


def get_one_worders(df):
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    one_word = Counter()
    total = Counter()

    for _, row in user_df.iterrows():
        total[row['sender']] += 1
        words = row['message'].split()
        if len(words) == 1:
            one_word[row['sender']] += 1

    one_word_stats = {}
    for sender, count in one_word.items():
        if total[sender] > 20:
            one_word_stats[sender] = {
                "count": count,
                "rate": round(count / total[sender] * 100, 1)
            }

    return dict(sorted(one_word_stats.items(), key=lambda x: x[1]['rate'], reverse=True)[:5])


def get_laugh_stats(df):
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    laugh_pattern = r'\b(lol|lmao|haha|hehe|rofl|😂|🤣|😹)\b'
    laugh_count = Counter()

    for _, row in user_df.iterrows():
        laughs = re.findall(laugh_pattern, row['message'].lower())
        laughs += [c for c in row['message'] if c in '😂🤣😹']
        if laughs:
            laugh_count[row['sender']] += len(laughs)

    return dict(laugh_count.most_common(5))


def get_streak_stats(df):
    user_df = df[~df['is_system']]

    if user_df.empty:
        return {"longest_streak": 0, "current_streak": 0}

    dates = sorted(user_df['date'].unique())

    if len(dates) < 2:
        return {"longest_streak": len(dates), "current_streak": len(dates)}

    longest = 1
    current = 1

    for i in range(1, len(dates)):
        diff = (dates[i] - dates[i-1]).days
        if diff == 1:
            current += 1
            longest = max(longest, current)
        elif diff > 1:
            current = 1

    return {
        "longest_streak": longest,
        "current_streak": current,
        "total_active_days": len(dates)
    }


def get_monologuers(df, min_streak=5):
    # consecutive msgs from same person
    user_df = df[~df['is_system']].sort_values('datetime')

    if len(user_df) < min_streak:
        return {}

    monologues = defaultdict(list)
    streak = 1
    prev_sender = None

    for _, row in user_df.iterrows():
        if row['sender'] == prev_sender:
            streak += 1
        else:
            if streak >= min_streak and prev_sender:
                monologues[prev_sender].append(streak)
            streak = 1
        prev_sender = row['sender']

    if streak >= min_streak and prev_sender:
        monologues[prev_sender].append(streak)

    mono_stats = {}
    for sender, streaks in monologues.items():
        mono_stats[sender] = {
            "longest": max(streaks),
            "total_monologues": len(streaks),
            "avg_length": round(sum(streaks) / len(streaks), 1)
        }

    return dict(sorted(mono_stats.items(), key=lambda x: x[1]['longest'], reverse=True)[:5])


def get_unique_words_per_person(df, top_n=10):
    # tf-idf style signature words
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    name_parts = set()
    for sender in user_df['sender'].unique():
        for part in sender.lower().split():
            if len(part) > 2:
                name_parts.add(part)

    person_words = defaultdict(Counter)
    all_words = Counter()

    for _, row in user_df.iterrows():
        clean_msg = re.sub(r'<[^>]+>', '', str(row['message']))
        clean_msg = re.sub(r'@\S+', '', clean_msg)

        words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_msg.lower())
        words = [w for w in words if w not in CHAT_STOP_WORDS and w not in name_parts]
        person_words[row['sender']].update(words)
        all_words.update(words)

    num_people = len(person_words)
    unique_words = {}

    for sender, words in person_words.items():
        total_words = sum(words.values())
        if total_words < 20:
            continue

        word_scores = {}
        for word, count in words.items():
            if count < 3:
                continue

            tf = count / total_words
            people_using = sum(1 for p in person_words.values() if word in p)
            idf = math.log(num_people / people_using) if people_using > 0 else 0

            # boost words this person uses way more
            personal_rate = count / all_words[word] if all_words[word] > 0 else 0

            score = tf * idf * (1 + personal_rate)
            word_scores[word] = {
                "score": round(score, 4),
                "count": count,
                "exclusivity": round(personal_rate * 100, 1)
            }

        top_words = sorted(word_scores.items(), key=lambda x: x[1]['score'], reverse=True)[:top_n]
        unique_words[sender] = dict(top_words)

    return unique_words


def get_catchphrases(df, min_occurrences=3):
    # 2-4 word phrases unique to each person
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    all_names = set()
    for sender in user_df['sender'].unique():
        name_lower = sender.lower()
        all_names.add(name_lower)
        for part in name_lower.split():
            if len(part) > 2:
                all_names.add(part)

    generic_phrases = {
        'in the', 'on the', 'to the', 'for the', 'and the', 'of the',
        'me and', 'you and', 'is the', 'it is', 'this is', 'that is',
        'i am', 'i was', 'i have', 'i will', 'i can', 'i think',
        'going to', 'want to', 'have to', 'need to', 'got to',
        'what is', 'what are', 'how is', 'how are', 'why is',
        'do you', 'are you', 'did you', 'can you', 'will you',
        'don know', 'don think', 'i don', 'you don',
        'it was', 'it will', 'there is', 'there are',
        'be like', 'would be', 'could be', 'will be',
    }

    person_phrases = defaultdict(Counter)
    all_phrases = Counter()

    for _, row in user_df.iterrows():
        msg = re.sub(r'@\u2068[^⁩]+\u2069', '', str(row['message']))
        msg = msg.lower()
        words = re.findall(r'\b[a-zA-Z]+\b', msg)

        for n in range(2, 5):
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i+n])
                if len(phrase) > 5:
                    if phrase in generic_phrases:
                        continue

                    phrase_words = set(phrase.split())
                    name_overlap = phrase_words & all_names
                    if len(name_overlap) >= len(phrase_words) - 1:
                        continue

                    person_phrases[row['sender']][phrase] += 1
                    all_phrases[phrase] += 1

    catchphrases = {}
    for sender, phrases in person_phrases.items():
        unique = []
        for phrase, count in phrases.most_common(50):
            if count >= min_occurrences:
                total = all_phrases[phrase]
                if count / total > 0.6:
                    unique.append({
                        "phrase": phrase,
                        "count": count,
                        "exclusivity": round(count / total * 100, 1)
                    })

        if unique:
            catchphrases[sender] = unique[:5]

    return catchphrases


def get_interesting_topics(df, top_n=15):
    # proper nouns, recurring themes etc
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    name_parts = set()
    for sender in user_df['sender'].unique():
        for part in sender.lower().split():
            if len(part) > 2:
                name_parts.add(part)

    word_counts = Counter()
    proper_noun_bonus = Counter()

    for _, row in user_df.iterrows():
        clean_msg = re.sub(r'<[^>]+>', '', str(row['message']))
        clean_msg = re.sub(r'@\S+', '', clean_msg)

        # capitalized = potential proper noun
        caps_words = set(re.findall(r'\b[A-Z][a-z]{2,}\b', clean_msg))

        words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_msg.lower())
        for w in words:
            if w not in TOPIC_ONLY_STOP_WORDS and w not in name_parts:
                word_counts[w] += 1
                if w.capitalize() in caps_words:
                    proper_noun_bonus[w] += 0.5

    scored_words = {}
    for word, count in word_counts.items():
        if count >= 3:
            score = count + proper_noun_bonus.get(word, 0)
            scored_words[word] = {"count": count, "score": score}

    sorted_topics = sorted(scored_words.items(), key=lambda x: x[1]['score'], reverse=True)
    return [word for word, _ in sorted_topics[:top_n]]


def get_group_vibe(df, emoji_stats, hourly_activity):
    user_df = df[~df['is_system']]

    vibe = {
        "energy": "medium",
        "topics": [],
        "personality": [],
        "peak_time": None,
        "description": ""
    }

    if user_df.empty:
        return vibe

    total_msgs = len(user_df)
    date_range = (user_df['date'].max() - user_df['date'].min()).days or 1
    msgs_per_day = total_msgs / date_range

    if msgs_per_day > 50:
        vibe["energy"] = "hyperactive"
        vibe["personality"].append("chaotic")
    elif msgs_per_day > 20:
        vibe["energy"] = "high"
        vibe["personality"].append("active")
    elif msgs_per_day > 5:
        vibe["energy"] = "medium"
        vibe["personality"].append("steady")
    else:
        vibe["energy"] = "chill"
        vibe["personality"].append("relaxed")

    if hourly_activity:
        peak_hour = max(hourly_activity, key=hourly_activity.get)
        if peak_hour < 6:
            vibe["peak_time"] = "late night degenerates"
            vibe["personality"].append("nocturnal")
        elif peak_hour < 12:
            vibe["peak_time"] = "morning people"
            vibe["personality"].append("productive")
        elif peak_hour < 18:
            vibe["peak_time"] = "afternoon chatters"
            vibe["personality"].append("casual")
        else:
            vibe["peak_time"] = "evening squad"
            vibe["personality"].append("social")

    vibe["topics"] = get_interesting_topics(df)

    if emoji_stats:
        top_emoji = list(emoji_stats.keys())[0] if emoji_stats else None
        if top_emoji in ['😂', '🤣', '😹']:
            vibe["personality"].append("humor-driven")
        elif top_emoji in ['😭', '😢', '😞']:
            vibe["personality"].append("dramatic")
        elif top_emoji in ['❤️', '🥰', '😍']:
            vibe["personality"].append("wholesome")
        elif top_emoji in ['🔥', '💯', '🙌']:
            vibe["personality"].append("hype")

    personality_str = ", ".join(vibe["personality"][:3])
    topics_str = ", ".join(vibe["topics"][:5]) if vibe["topics"] else "everything and nothing"

    vibe["description"] = f"A {vibe['energy']} energy group of {personality_str} folks who mostly talk about {topics_str}."

    return vibe
