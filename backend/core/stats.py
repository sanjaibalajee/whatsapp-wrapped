# stats - all the number crunching

import re
import math
import numpy as np
from datetime import timedelta
from collections import Counter, defaultdict

from .constants import CHAT_STOP_WORDS, TOPIC_ONLY_STOP_WORDS
from .parser import extract_emojis


def format_duration(seconds):
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"


def get_basic_stats(df, user_df=None):
    if user_df is None:
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


def get_top_chatters(df, user_df=None, top_n=10):
    if user_df is None:
        user_df = df[~df['is_system']]
    counts = user_df['sender'].value_counts().head(top_n)
    return counts.to_dict()


def get_hourly_activity(df, user_df=None):
    if user_df is None:
        user_df = df[~df['is_system']]
    return user_df['hour'].value_counts().sort_index().to_dict()


def get_daily_activity(df, user_df=None):
    if user_df is None:
        user_df = df[~df['is_system']]
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    counts = user_df['day_of_week'].value_counts()
    return {day: counts.get(day, 0) for day in day_order}


def get_emoji_stats(df, user_df=None, top_n=15):
    if user_df is None:
        user_df = df[~df['is_system']]

    # vectorized - apply extract_emojis to all messages at once
    all_emojis = user_df['message'].apply(lambda x: extract_emojis(str(x))).explode()
    all_emojis = all_emojis.dropna()

    if all_emojis.empty:
        return {}

    return dict(all_emojis.value_counts().head(top_n).to_dict())


def get_emoji_stats_by_user(df, user_df=None, top_n=5):
    if user_df is None:
        user_df = df[~df['is_system']]

    # vectorized extraction
    emoji_series = user_df[['sender', 'message']].copy()
    emoji_series['emojis'] = emoji_series['message'].apply(lambda x: extract_emojis(str(x)))

    user_emojis = {}
    for sender in emoji_series['sender'].unique():
        sender_emojis = emoji_series[emoji_series['sender'] == sender]['emojis']
        all_emojis = [e for elist in sender_emojis for e in elist]

        if all_emojis:
            user_emojis[sender] = {
                "total": len(all_emojis),
                "top": dict(Counter(all_emojis).most_common(3))
            }

    return dict(sorted(user_emojis.items(), key=lambda x: x[1]['total'], reverse=True)[:top_n])


def get_media_stats(df, user_df=None):
    if user_df is None:
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


def get_word_stats(df, user_df=None, top_n=20):
    if user_df is None:
        user_df = df[~df['is_system']]
    text_df = user_df[user_df['media_type'].isna()]

    # filter out participant names
    name_parts = set()
    for sender in text_df['sender'].unique():
        for part in sender.lower().split():
            if len(part) > 2:
                name_parts.add(part)

    # vectorized word extraction
    def extract_words(msg):
        clean = re.sub(r'<[^>]+>', '', str(msg))
        clean = re.sub(r'@\S+', '', clean)
        return [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', clean.lower())
                if w not in CHAT_STOP_WORDS and w not in name_parts]

    all_words = text_df['message'].apply(extract_words).explode().dropna()
    return dict(all_words.value_counts().head(top_n).to_dict())


def get_conversation_starters(df, user_df=None, gap_minutes=60):
    if user_df is None:
        user_df = df[~df['is_system']]
    sorted_df = user_df.sort_values('datetime').copy()

    if len(sorted_df) < 2:
        return {}

    # vectorized with shift - compare each row to previous
    sorted_df['prev_time'] = sorted_df['datetime'].shift(1)
    sorted_df['time_gap'] = (sorted_df['datetime'] - sorted_df['prev_time']).dt.total_seconds() / 60

    # first msg or gap > threshold = conversation starter
    starters_mask = sorted_df['prev_time'].isna() | (sorted_df['time_gap'] > gap_minutes)
    starters = sorted_df.loc[starters_mask, 'sender'].value_counts().head(10)

    return starters.to_dict()


def get_night_owls(df, user_df=None):
    # 12am-5am crew
    if user_df is None:
        user_df = df[~df['is_system']]
    night_df = user_df[(user_df['hour'] >= 0) & (user_df['hour'] < 5)]

    if night_df.empty:
        return {}

    return night_df['sender'].value_counts().head(5).to_dict()


def get_early_birds(df, user_df=None):
    # 5am-8am gang
    if user_df is None:
        user_df = df[~df['is_system']]
    morning_df = user_df[(user_df['hour'] >= 5) & (user_df['hour'] < 8)]

    if morning_df.empty:
        return {}

    return morning_df['sender'].value_counts().head(5).to_dict()


def get_longest_messages(df, user_df=None, top_n=5):
    if user_df is None:
        user_df = df[~df['is_system']]
    text_df = user_df[user_df['media_type'].isna()]

    avg_length = text_df.groupby('sender')['char_count'].mean()
    return avg_length.nlargest(top_n).to_dict()


def get_busiest_dates(df, user_df=None, top_n=5):
    if user_df is None:
        user_df = df[~df['is_system']]
    # use datetime to ensure year filter is respected
    date_counts = user_df.groupby(user_df['datetime'].dt.date).size()
    return date_counts.nlargest(top_n).to_dict()


def get_response_pairs(df, user_df=None, window_minutes=5):
    # who replies to whom - vectorized with shift
    if user_df is None:
        user_df = df[~df['is_system']]
    sorted_df = user_df.sort_values('datetime').copy()

    if len(sorted_df) < 2:
        return {}

    # compare each row to previous using shift
    sorted_df['prev_sender'] = sorted_df['sender'].shift(1)
    sorted_df['prev_time'] = sorted_df['datetime'].shift(1)
    sorted_df['time_gap'] = (sorted_df['datetime'] - sorted_df['prev_time']).dt.total_seconds() / 60

    # valid response = different sender, within time window
    response_mask = (
        sorted_df['prev_sender'].notna() &
        (sorted_df['sender'] != sorted_df['prev_sender']) &
        (sorted_df['time_gap'] <= window_minutes)
    )

    responses = sorted_df.loc[response_mask, ['prev_sender', 'sender']]
    if responses.empty:
        return {}

    # count pairs
    pair_counts = responses.groupby(['prev_sender', 'sender']).size()
    top_pairs = pair_counts.nlargest(10)

    return {(idx[0], idx[1]): count for idx, count in top_pairs.items()}


def get_double_texters(df, user_df=None):
    # msgs in a row before reply - vectorized
    if user_df is None:
        user_df = df[~df['is_system']]
    sorted_df = user_df.sort_values('datetime').copy()

    if len(sorted_df) < 2:
        return {}

    # mark where sender changes
    sorted_df['prev_sender'] = sorted_df['sender'].shift(1)
    sorted_df['sender_changed'] = sorted_df['sender'] != sorted_df['prev_sender']

    # create streak groups - cumsum increments at each sender change
    sorted_df['streak_group'] = sorted_df['sender_changed'].cumsum()

    # count msgs per streak, grouped by sender
    streak_counts = sorted_df.groupby(['streak_group', 'sender']).size().reset_index(name='streak_len')

    # double text = streak length - 1 (first msg isn't a double text)
    streak_counts['double_texts'] = (streak_counts['streak_len'] - 1).clip(lower=0)

    # sum up per sender
    double_texts = streak_counts.groupby('sender')['double_texts'].sum()
    double_texts = double_texts[double_texts > 0].nlargest(10)

    return double_texts.to_dict()


def get_conversation_killers(df, user_df=None, silence_minutes=30):
    # whose msgs end convos - vectorized
    if user_df is None:
        user_df = df[~df['is_system']]
    sorted_df = user_df.sort_values('datetime').copy()

    if len(sorted_df) < 2:
        return {}

    # time to next message
    sorted_df['next_time'] = sorted_df['datetime'].shift(-1)
    sorted_df['gap_to_next'] = (sorted_df['next_time'] - sorted_df['datetime']).dt.total_seconds() / 60

    # kills = gap > threshold (exclude last msg)
    sorted_df['is_killer'] = sorted_df['gap_to_next'] > silence_minutes

    # count totals and kills per sender
    total_msgs = sorted_df.groupby('sender').size()
    kills = sorted_df[sorted_df['is_killer']].groupby('sender').size()

    kill_rates = {}
    for sender in kills.index:
        if total_msgs[sender] > 10:
            kill_rates[sender] = {
                "kills": int(kills[sender]),
                "total": int(total_msgs[sender]),
                "rate": round(kills[sender] / total_msgs[sender] * 100, 1)
            }

    return dict(sorted(kill_rates.items(), key=lambda x: x[1]['kills'], reverse=True)[:5])


def get_response_times(df, user_df=None):
    # vectorized response time calculation
    if user_df is None:
        user_df = df[~df['is_system']]
    sorted_df = user_df.sort_values('datetime').copy()

    if len(sorted_df) < 2:
        return {}

    # compare to previous message using shift
    sorted_df['prev_sender'] = sorted_df['sender'].shift(1)
    sorted_df['prev_time'] = sorted_df['datetime'].shift(1)
    sorted_df['gap_seconds'] = (sorted_df['datetime'] - sorted_df['prev_time']).dt.total_seconds()

    # valid response = different sender, within 1 hour
    response_mask = (
        sorted_df['prev_sender'].notna() &
        (sorted_df['sender'] != sorted_df['prev_sender']) &
        (sorted_df['gap_seconds'] > 0) &
        (sorted_df['gap_seconds'] < 3600)
    )

    responses = sorted_df.loc[response_mask, ['sender', 'gap_seconds']]

    # aggregate per sender
    response_stats = responses.groupby('sender')['gap_seconds'].agg(['mean', 'count'])
    response_stats = response_stats[response_stats['count'] >= 5]

    avg_times = {}
    for sender, row in response_stats.iterrows():
        avg_seconds = row['mean']
        avg_times[sender] = {
            "avg_seconds": round(avg_seconds, 1),
            "avg_formatted": format_duration(avg_seconds),
            "response_count": int(row['count'])
        }

    return dict(sorted(avg_times.items(), key=lambda x: x[1]['avg_seconds'])[:10])


def get_caps_users(df, user_df=None):
    # WHO TYPES LIKE THIS - vectorized
    if user_df is None:
        user_df = df[~df['is_system']]
    text_df = user_df[user_df['media_type'].isna()].copy()

    if text_df.empty:
        return {}

    # count letters and caps in each message
    def calc_caps_ratio(msg):
        letters = re.findall(r'[a-zA-Z]', str(msg))
        if len(letters) < 5:
            return None
        caps = len(re.findall(r'[A-Z]', str(msg)))
        return caps / len(letters)

    text_df['caps_ratio'] = text_df['message'].apply(calc_caps_ratio)
    valid_df = text_df[text_df['caps_ratio'].notna()]

    # count total and caps msgs per sender
    total_per_sender = valid_df.groupby('sender').size()
    caps_df = valid_df[valid_df['caps_ratio'] > 0.7]
    caps_per_sender = caps_df.groupby('sender').size()

    caps_rates = {}
    for sender in caps_per_sender.index:
        if total_per_sender.get(sender, 0) > 10:
            caps_rates[sender] = {
                "caps_messages": int(caps_per_sender[sender]),
                "rate": round(caps_per_sender[sender] / total_per_sender[sender] * 100, 1)
            }

    return dict(sorted(caps_rates.items(), key=lambda x: x[1]['caps_messages'], reverse=True)[:5])


def get_question_askers(df, user_df=None):
    # vectorized question counting
    if user_df is None:
        user_df = df[~df['is_system']]
    text_df = user_df[user_df['media_type'].isna()].copy()

    if text_df.empty:
        return {}

    # vectorized: check if message contains ?
    text_df['has_question'] = text_df['message'].str.contains(r'\?', regex=True, na=False)

    total = text_df.groupby('sender').size()
    questions = text_df[text_df['has_question']].groupby('sender').size()

    question_stats = {}
    for sender in questions.index:
        if total.get(sender, 0) > 10:
            question_stats[sender] = {
                "questions": int(questions[sender]),
                "rate": round(questions[sender] / total[sender] * 100, 1)
            }

    return dict(sorted(question_stats.items(), key=lambda x: x[1]['questions'], reverse=True)[:5])


def get_link_sharers(df, user_df=None):
    # vectorized link counting
    if user_df is None:
        user_df = df[~df['is_system']]
    text_df = user_df[user_df['media_type'].isna()].copy()

    if text_df.empty:
        return {}

    url_pattern = r'https?://\S+'
    text_df['link_count'] = text_df['message'].str.count(url_pattern)

    link_counts = text_df.groupby('sender')['link_count'].sum()
    link_counts = link_counts[link_counts > 0].nlargest(5)

    return link_counts.to_dict()


def get_one_worders(df, user_df=None):
    # vectorized one-word message counting
    if user_df is None:
        user_df = df[~df['is_system']]
    text_df = user_df[user_df['media_type'].isna()].copy()

    if text_df.empty:
        return {}

    text_df['word_count_actual'] = text_df['message'].str.split().str.len()
    text_df['is_one_word'] = text_df['word_count_actual'] == 1

    total = text_df.groupby('sender').size()
    one_word = text_df[text_df['is_one_word']].groupby('sender').size()

    one_word_stats = {}
    for sender in one_word.index:
        if total.get(sender, 0) > 20:
            one_word_stats[sender] = {
                "count": int(one_word[sender]),
                "rate": round(one_word[sender] / total[sender] * 100, 1)
            }

    return dict(sorted(one_word_stats.items(), key=lambda x: x[1]['rate'], reverse=True)[:5])


def get_laugh_stats(df, user_df=None):
    # vectorized laugh counting
    if user_df is None:
        user_df = df[~df['is_system']]
    text_df = user_df[user_df['media_type'].isna()].copy()

    if text_df.empty:
        return {}

    laugh_pattern = r'\b(lol|lmao|haha|hehe|rofl)\b'

    def count_laughs(msg):
        msg_str = str(msg).lower()
        text_laughs = len(re.findall(laugh_pattern, msg_str))
        emoji_laughs = sum(1 for c in msg_str if c in '😂🤣😹')
        return text_laughs + emoji_laughs

    text_df['laugh_count'] = text_df['message'].apply(count_laughs)
    laugh_counts = text_df.groupby('sender')['laugh_count'].sum()
    laugh_counts = laugh_counts[laugh_counts > 0].nlargest(5)

    return laugh_counts.to_dict()


def get_streak_stats(df, user_df=None):
    if user_df is None:
        user_df = df[~df['is_system']]

    if user_df.empty:
        return {"longest_streak": 0, "current_streak": 0}

    dates = sorted(user_df['date'].unique())

    if len(dates) < 2:
        return {"longest_streak": len(dates), "current_streak": len(dates)}

    # vectorized streak calculation using numpy
    import pandas as pd
    date_series = pd.Series(dates)
    diffs = date_series.diff().dt.days.fillna(1)

    # find streak boundaries
    streak_breaks = (diffs != 1).cumsum()
    streak_lengths = streak_breaks.groupby(streak_breaks).size()

    longest = int(streak_lengths.max())
    current = int(streak_lengths.iloc[-1])

    return {
        "longest_streak": longest,
        "current_streak": current,
        "total_active_days": len(dates)
    }


def get_monologuers(df, user_df=None, min_streak=5):
    # consecutive msgs from same person - vectorized
    if user_df is None:
        user_df = df[~df['is_system']]
    sorted_df = user_df.sort_values('datetime').copy()

    if len(sorted_df) < min_streak:
        return {}

    # reuse the streak grouping logic from double_texters
    sorted_df['prev_sender'] = sorted_df['sender'].shift(1)
    sorted_df['sender_changed'] = sorted_df['sender'] != sorted_df['prev_sender']
    sorted_df['streak_group'] = sorted_df['sender_changed'].cumsum()

    # count msgs per streak
    streak_counts = sorted_df.groupby(['streak_group', 'sender']).size().reset_index(name='streak_len')

    # filter to monologue-length streaks
    monologue_streaks = streak_counts[streak_counts['streak_len'] >= min_streak]

    if monologue_streaks.empty:
        return {}

    mono_stats = {}
    for sender in monologue_streaks['sender'].unique():
        sender_streaks = monologue_streaks[monologue_streaks['sender'] == sender]['streak_len']
        mono_stats[sender] = {
            "longest": int(sender_streaks.max()),
            "total_monologues": len(sender_streaks),
            "avg_length": round(sender_streaks.mean(), 1)
        }

    return dict(sorted(mono_stats.items(), key=lambda x: x[1]['longest'], reverse=True)[:5])


def get_unique_words_per_person(df, user_df=None, top_n=10):
    # tf-idf style signature words - optimized
    if user_df is None:
        user_df = df[~df['is_system']]
    text_df = user_df[user_df['media_type'].isna()].copy()

    if text_df.empty:
        return {}

    name_parts = set()
    for sender in text_df['sender'].unique():
        for part in sender.lower().split():
            if len(part) > 2:
                name_parts.add(part)

    # extract words vectorized
    def extract_clean_words(msg):
        clean = re.sub(r'<[^>]+>', '', str(msg))
        clean = re.sub(r'@\S+', '', clean)
        return [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', clean.lower())
                if w not in CHAT_STOP_WORDS and w not in name_parts]

    text_df['words'] = text_df['message'].apply(extract_clean_words)

    # build word counts per person
    person_words = defaultdict(Counter)
    all_words = Counter()

    for sender in text_df['sender'].unique():
        sender_words = text_df[text_df['sender'] == sender]['words']
        word_list = [w for words in sender_words for w in words]
        person_words[sender].update(word_list)
        all_words.update(word_list)

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


def get_catchphrases(df, user_df=None, min_occurrences=3):
    # 2-4 word phrases unique to each person - optimized
    if user_df is None:
        user_df = df[~df['is_system']]
    text_df = user_df[user_df['media_type'].isna()].copy()

    if text_df.empty:
        return {}

    all_names = set()
    for sender in text_df['sender'].unique():
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

    def extract_phrases(msg):
        msg = re.sub(r'@\u2068[^⁩]+\u2069', '', str(msg)).lower()
        words = re.findall(r'\b[a-zA-Z]+\b', msg)
        phrases = []
        for n in range(2, 5):
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i+n])
                if len(phrase) > 5 and phrase not in generic_phrases:
                    phrase_words = set(phrase.split())
                    if len(phrase_words & all_names) < len(phrase_words) - 1:
                        phrases.append(phrase)
        return phrases

    text_df['phrases'] = text_df['message'].apply(extract_phrases)

    person_phrases = defaultdict(Counter)
    all_phrases = Counter()

    for sender in text_df['sender'].unique():
        sender_phrases = text_df[text_df['sender'] == sender]['phrases']
        phrase_list = [p for phrases in sender_phrases for p in phrases]
        person_phrases[sender].update(phrase_list)
        all_phrases.update(phrase_list)

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


def get_interesting_topics(df, user_df=None, top_n=15):
    # proper nouns, recurring themes etc - optimized
    if user_df is None:
        user_df = df[~df['is_system']]
    text_df = user_df[user_df['media_type'].isna()].copy()

    if text_df.empty:
        return []

    name_parts = set()
    for sender in text_df['sender'].unique():
        for part in sender.lower().split():
            if len(part) > 2:
                name_parts.add(part)

    def extract_topics(msg):
        clean = re.sub(r'<[^>]+>', '', str(msg))
        clean = re.sub(r'@\S+', '', clean)
        caps_words = set(re.findall(r'\b[A-Z][a-z]{2,}\b', clean))
        words = re.findall(r'\b[a-zA-Z]{3,}\b', clean.lower())
        return [(w, w.capitalize() in caps_words) for w in words
                if w not in TOPIC_ONLY_STOP_WORDS and w not in name_parts]

    text_df['topics'] = text_df['message'].apply(extract_topics)

    word_counts = Counter()
    proper_noun_bonus = Counter()

    for topics in text_df['topics']:
        for word, is_caps in topics:
            word_counts[word] += 1
            if is_caps:
                proper_noun_bonus[word] += 0.5

    scored_words = {}
    for word, count in word_counts.items():
        if count >= 3:
            score = count + proper_noun_bonus.get(word, 0)
            scored_words[word] = {"count": count, "score": score}

    sorted_topics = sorted(scored_words.items(), key=lambda x: x[1]['score'], reverse=True)
    return [word for word, _ in sorted_topics[:top_n]]


def get_group_vibe(df, emoji_stats, hourly_activity, user_df=None, full=False):
    if user_df is None:
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

    # get more topics in full mode
    vibe["topics"] = get_interesting_topics(df, user_df, top_n=30 if full else 15)

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
