import re
import math
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box
import emoji
import json

console = Console()

# System messages to filter out
SYSTEM_PATTERNS = [
    "Messages and calls are end-to-end encrypted",
    "created group",
    "added you",
    "left the group",
    "removed",
    "changed the group",
    "You're now an admin",
    "You're no longer an admin",
    "changed this group's icon",
    "deleted this group's icon",
    "changed the subject",
    "joined using this group's invite link",
]

# Senders to ignore (bots, etc.)
IGNORED_SENDERS = [
    "Meta AI",
]

MEDIA_PATTERNS = {
    "image": "image omitted",
    "video": "video omitted",
    "audio": "audio omitted",
    "sticker": "sticker omitted",
    "gif": "GIF omitted",
    "document": "document omitted",
    "contact": "contact card omitted",
    "location": "location omitted",
}

# Comprehensive stop words for chat analysis
CHAT_STOP_WORDS = {
    # Basic English
    'the', 'a', 'an', 'is', 'it', 'to', 'of', 'and', 'in', 'for', 'on',
    'with', 'as', 'at', 'by', 'this', 'that', 'i', 'you', 'he', 'she',
    'we', 'they', 'me', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
    'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
    'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'get', 'got',
    'but', 'or', 'if', 'then', 'so', 'just', 'now', 'here', 'there',
    'what', 'who', 'how', 'when', 'where', 'why', 'which', 'whom', 'whose',
    'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'than', 'too', 'very',
    'any', 'much', 'many', 'else', 'either', 'neither', 'whether', 'ever',
    'once', 'twice', 'lot', 'lots', 'bit', 'little', 'less', 'least',

    # Common verbs
    'go', 'going', 'went', 'gone', 'come', 'came', 'coming', 'take', 'took',
    'taken', 'taking', 'make', 'made', 'making', 'get', 'got', 'getting',
    'see', 'saw', 'seen', 'seeing', 'know', 'knew', 'known', 'knowing',
    'think', 'thought', 'thinking', 'want', 'wanted', 'wanting',
    'say', 'said', 'saying', 'tell', 'told', 'telling', 'ask', 'asked',
    'try', 'tried', 'trying', 'let', 'put', 'give', 'gave', 'given',
    'look', 'looked', 'looking', 'find', 'found', 'finding',
    'use', 'used', 'using', 'keep', 'kept', 'keeping',
    'start', 'started', 'starting', 'stop', 'stopped', 'stopping',
    'send', 'sent', 'sending', 'read', 'reading', 'write', 'writing',
    'call', 'called', 'calling', 'reply', 'replied', 'replying',
    'wait', 'waiting', 'leave', 'left', 'leaving', 'stay', 'staying',
    'change', 'changed', 'changing', 'meet', 'met', 'meeting',
    'feel', 'felt', 'feeling', 'seems', 'seem', 'seemed',

    # Common adjectives/adverbs
    'good', 'bad', 'best', 'better', 'worse', 'worst', 'great', 'nice',
    'right', 'wrong', 'true', 'false', 'real', 'fake', 'new', 'old',
    'big', 'small', 'long', 'short', 'high', 'low', 'first', 'last',
    'next', 'early', 'late', 'fast', 'slow', 'easy', 'hard', 'sure',
    'well', 'back', 'even', 'still', 'also', 'again', 'already', 'always',
    'never', 'maybe', 'probably', 'actually', 'really', 'literally',
    'basically', 'definitely', 'exactly', 'honestly', 'seriously',
    'apparently', 'obviously', 'totally', 'completely', 'absolutely',

    # Common nouns
    'thing', 'things', 'stuff', 'time', 'times', 'day', 'days', 'night',
    'week', 'month', 'year', 'hour', 'minute', 'place', 'way', 'case',
    'point', 'part', 'side', 'end', 'fact', 'life', 'world', 'home',
    'work', 'job', 'people', 'person', 'guy', 'girl', 'man', 'woman',
    'friend', 'friends', 'everyone', 'someone', 'anyone', 'nobody',
    'everything', 'something', 'anything', 'nothing',
    'today', 'tomorrow', 'yesterday', 'morning', 'evening', 'afternoon',
    'money', 'phone', 'office', 'college', 'school', 'class', 'exam',
    'food', 'water', 'sleep', 'movie', 'game', 'song', 'photo', 'pic',
    'plan', 'idea', 'problem', 'issue', 'reason', 'question', 'answer',
    'text', 'chat', 'group', 'link', 'post', 'comment', 'reply',
    'free', 'busy', 'late', 'early', 'soon', 'later', 'online', 'offline',
    'out', 'inside', 'outside', 'near', 'far', 'close', 'open', 'done',
    'buy', 'sell', 'pay', 'cost', 'price', 'order', 'book', 'check',

    # Numbers
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',

    # Pronouns and determiners
    'him', 'them', 'us', 'from', 'into', 'onto', 'upon', 'about', 'after',
    'before', 'between', 'through', 'during', 'under', 'over', 'above', 'below',

    # Chat/internet slang (common across all chats)
    'lol', 'lmao', 'lmfao', 'rofl', 'haha', 'hehe', 'hihi', 'omg', 'wtf',
    'idk', 'idc', 'idgaf', 'tbh', 'ngl', 'imo', 'imho', 'fyi', 'btw', 'afaik',
    'smh', 'ffs', 'jk', 'irl', 'tho', 'tho', 'rn', 'atm', 'asap',
    'ppl', 'pls', 'plz', 'thx', 'ty', 'np', 'nvm', 'ofc', 'obv',
    'gonna', 'wanna', 'gotta', 'kinda', 'sorta', 'lemme', 'gimme', 'dunno',
    'wat', 'wut', 'abt', 'abt', 'thats', 'whats', 'hows', 'whos',
    'shud', 'cud', 'wud', 'chk', 'pls', 'msg', 'msgs', 'rply',
    'tom', 'tmrw', 'tmr', 'tomo', 'yday', 'ytd', 'yest',
    'summa', 'somn', 'smth', 'smthn', 'sumn', 'alone', 'full', 'half',
    'coz', 'cos', 'cuz', 'bcoz', 'bcuz', 'bcz', 'bc', 'because',
    'dont', 'didnt', 'wont', 'cant', 'shouldnt', 'wouldnt', 'couldnt',
    'isnt', 'arent', 'wasnt', 'werent', 'havent', 'hasnt', 'hadnt',
    'doing', 'eating', 'going', 'coming', 'seeing', 'saying', 'asking',
    'eat', 'ate', 'eaten', 'drink', 'drank', 'drunk', 'play', 'played',
    'room', 'rooms', 'unit', 'units', 'house', 'home', 'hostel', 'floor',
    'ok', 'okay', 'okk', 'okkk', 'okayy', 'okayyy', 'kay', 'kk', 'kkk',
    'yes', 'yea', 'yeah', 'yeahh', 'yess', 'yesss', 'yup', 'yep', 'yeppp',
    'no', 'nah', 'nope', 'noo', 'nooo',
    'hmm', 'hmmm', 'umm', 'ummm', 'uhh', 'uhhh', 'ahh', 'ahhh', 'ohh', 'ohhh',
    'aha', 'oho', 'wow', 'woww', 'woah', 'whoa', 'damn', 'dang', 'darn',
    'bro', 'bruh', 'bruhhh', 'dude', 'man', 'boi', 'boii', 'gal', 'sis',
    'guys', 'yall', 'fam', 'homie', 'bestie', 'babe', 'bby', 'hun',
    'sir', 'mam', 'miss', 'mrs', 'mama', 'papa', 'mom', 'dad',
    'shit', 'crap', 'fuck', 'hell', 'ass', 'bitch', 'wtf', 'wth',
    'cool', 'lit', 'fire', 'sick', 'dope', 'nice', 'noice', 'awesome',
    'super', 'ultra', 'mega', 'hyper', 'extra',
    'love', 'hate', 'like', 'thank', 'thanks', 'sorry', 'please',
    'bye', 'byee', 'byeee', 'cya', 'ttyl', 'gn', 'gm', 'gtg',
    'hii', 'hiii', 'hiiii', 'hey', 'heyy', 'heyyy', 'hello', 'helloo',
    'wya', 'wyd', 'hru', 'hbu', 'sup', 'wassup', 'whatsup',

    # Common Tamil chat words (universal, not signature)
    'da', 'di', 'na', 'la', 'ha', 'ya', 'ra', 'pa', 'ma', 'va',
    'dei', 'dai', 'dey', 'ada', 'adi', 'illa', 'enna', 'epdi', 'enga',
    'seri', 'sari', 'ok', 'hmm', 'aama', 'aana', 'appo', 'ippo',
    'nee', 'naan', 'avan', 'aval', 'anga', 'inga', 'thaan', 'dhaan',
    'kandipa', 'paru', 'sollu', 'sollren', 'sollura', 'pannren', 'pannura',

    # More generic English
    'mean', 'means', 'meant', 'meaning', 'type', 'types', 'kind', 'kinds',
    'sort', 'sorts', 'form', 'forms', 'level', 'levels', 'part', 'parts',

    # Contraction remnants
    'don', 'didn', 'won', 'wouldn', 'couldn', 'shouldn', 'isn', 'aren',
    'wasn', 'weren', 'hasn', 'haven', 'hadn', 'doesn', 'ain',
    'll', 've', 're', 'nt', 'em', 'ill', 'ull', 'yall',

    # Time-related
    'mins', 'min', 'hrs', 'secs', 'sec', 'hour', 'hours', 'minute', 'minutes',
    'second', 'seconds', 'week', 'weeks', 'month', 'months', 'year', 'years',
    'daily', 'weekly', 'monthly', 'yearly', 'ago', 'later', 'soon',

    # Activity words
    'watch', 'watched', 'watching', 'listen', 'listened', 'listening',
    'dinner', 'lunch', 'breakfast', 'snack', 'snacks', 'brunch',

    # WhatsApp/System words
    'message', 'messages', 'edited', 'deleted', 'omitted', 'media',
    'image', 'video', 'audio', 'sticker', 'gif', 'document', 'contact',
    'https', 'http', 'www', 'com', 'org', 'net', 'meta', 'whatsapp',
}

# Additional words to filter ONLY from topics (not from signature words)
# These are fun slang that might be interesting in personal stats but not as "Hot Topics"
TOPIC_ONLY_STOP_WORDS = CHAT_STOP_WORDS | {
    # Tamil slang/exclamations - fun in personal stats, not topics
    'poda', 'podi', 'poda', 'poyi', 'po', 'vada', 'vadi',
    'da', 'dei', 'di', 'dey', 'ra', 'ri',
    'aiyo', 'aiyoo', 'aiyyoo', 'chee', 'chi', 'cha',
    'machaan', 'macha', 'machan', 'thala', 'anna', 'akka',
    'enna', 'ethu', 'yaaru', 'yaar', 'yen', 'enga', 'epdi', 'eppadi',
    # Common expressions that aren't topics
    'bro', 'bruh', 'dude', 'man', 'guys',
    'sad', 'happy', 'nice', 'cool', 'lol', 'haha',
}


def parse_whatsapp(file_path):
    """Parse WhatsApp chat export file."""
    # Regex for: [DD/MM/YY, HH:MM:SS AM/PM] Sender: Content
    pattern = r'^\[(\d{2}/\d{2}/\d{2}),\s(\d{1,2}:\d{2}:\d{2}\s[APM]{2})\]\s([^:]+):\s(.*)$'

    data = []

    with open(file_path, 'r', encoding='utf-8') as f:
        current_message = None

        for line in f:
            # Remove left-to-right mark and strip
            line = line.replace('\u200e', '').strip()

            if not line:
                continue

            match = re.match(pattern, line)

            if match:
                # Save previous message if exists
                if current_message:
                    data.append(current_message)

                date_str, time_str, sender, content = match.groups()

                # Parse datetime
                msg_date = datetime.strptime(date_str, '%d/%m/%y')
                msg_time = datetime.strptime(time_str, '%I:%M:%S %p')

                full_datetime = msg_date.replace(
                    hour=msg_time.hour,
                    minute=msg_time.minute,
                    second=msg_time.second
                )

                # Check if system message or ignored sender
                is_system = any(p in content for p in SYSTEM_PATTERNS) or sender.strip() in IGNORED_SENDERS

                # Check media type
                media_type = None
                for media, pattern_text in MEDIA_PATTERNS.items():
                    if pattern_text in content:
                        media_type = media
                        break

                current_message = {
                    "datetime": full_datetime,
                    "date": msg_date.date(),
                    "time": msg_time.time(),
                    "hour": msg_time.hour,
                    "day_of_week": msg_date.strftime('%A'),
                    "sender": sender.strip(),
                    "message": content,
                    "is_system": is_system,
                    "media_type": media_type,
                    "word_count": len(content.split()) if not is_system and not media_type else 0,
                    "char_count": len(content) if not is_system and not media_type else 0,
                }
            else:
                # Multi-line message continuation
                if current_message:
                    current_message["message"] += "\n" + line
                    current_message["word_count"] += len(line.split())
                    current_message["char_count"] += len(line)

        # Don't forget the last message
        if current_message:
            data.append(current_message)

    return pd.DataFrame(data)


def detect_group_names(df):
    """
    Detect group names that appear as "senders" in system messages.
    In WhatsApp, the group name appears as the sender for system messages like
    "You created group", "You changed the group name to", etc.

    Returns: (df, group_names_set, current_group_name)
    """
    if df.empty:
        return df, set(), None

    # Patterns that indicate system messages (group name is the sender)
    group_system_patterns = [
        "You created group",
        "You changed the group name",
        "You changed this group",
        "You changed the subject",
        "You changed the settings",
        "Messages and calls are end-to-end encrypted",
        "Only messages that mention",
        "added you",
        "removed you",
        "left",
        "joined using this group",
        "changed the group",
        "You're now an admin",
        "can be read by Meta",
        "allow only admins",
    ]

    group_names = set()
    current_group_name = None
    group_name_history = []

    # Check each unique sender
    for sender in df['sender'].unique():
        sender_df = df[df['sender'] == sender]

        # Check if ALL messages from this sender are system messages
        all_system = True
        for _, row in sender_df.iterrows():
            msg = str(row['message'])
            is_system_msg = any(pattern.lower() in msg.lower() for pattern in group_system_patterns)
            if not is_system_msg and not row['is_system']:
                all_system = False
                break

        if all_system and len(sender_df) > 0:
            group_names.add(sender)

            # Extract group name history from "You changed the group name to" messages
            for _, row in sender_df.iterrows():
                msg = str(row['message'])

                # Pattern: You changed the group name to "NEW NAME"
                # Note: WhatsApp uses curly quotes U+201C (") and U+201D (")
                name_match = re.search(r'changed the group name to [""\u201C](.+?)[""\u201D]', msg)
                if name_match:
                    new_name = name_match.group(1)
                    group_name_history.append({
                        'name': new_name,
                        'date': row['datetime']
                    })

                # Pattern: You created group "NAME"
                create_match = re.search(r'created group [""\u201C](.+?)[""\u201D]', msg)
                if create_match:
                    new_name = create_match.group(1)
                    group_name_history.insert(0, {
                        'name': new_name,
                        'date': row['datetime']
                    })

    # Get current group name (most recent)
    if group_name_history:
        group_name_history.sort(key=lambda x: x['date'])
        current_group_name = group_name_history[-1]['name']
        print(f"  Group name: '{current_group_name}'")
        if len(group_name_history) > 1:
            print(f"  (renamed {len(group_name_history)} times)")

    # Also detect system-like senders
    for sender in df['sender'].unique():
        if sender.lower() in ['you', 'group', 'admin']:
            group_names.add(sender)

    if group_names:
        for name in group_names:
            if name != current_group_name:  # Don't print group name twice
                count = len(df[df['sender'] == name])
                print(f"  Filtered sender: '{name}' ({count} msgs)")

    # Mark these as system messages
    if group_names:
        df = df.copy()
        df.loc[df['sender'].isin(group_names), 'is_system'] = True

    return df, group_names, current_group_name


def merge_similar_contacts(df):
    """
    Merge contacts that are the same person with different names.
    Detects renamed contacts (e.g., "Sanjjit S CSE G2 SSN" -> "Sanjjit S")
    """
    if df.empty:
        return df

    senders = df['sender'].unique().tolist()

    # Build mapping of old names to canonical names
    name_mapping = {}

    for i, name1 in enumerate(senders):
        if name1 in name_mapping:
            continue

        for name2 in senders[i+1:]:
            if name2 in name_mapping:
                continue

            # Normalize for comparison
            n1_lower = name1.lower().strip()
            n2_lower = name2.lower().strip()

            # Check if one is a prefix of the other (common in contact renames)
            # "Sanjjit S" is prefix of "Sanjjit S CSE G2 SSN"
            if n1_lower.startswith(n2_lower) or n2_lower.startswith(n1_lower):
                # Use the shorter name as canonical (usually the newer/cleaner name)
                if len(name1) <= len(name2):
                    canonical, old = name1, name2
                else:
                    canonical, old = name2, name1

                name_mapping[old] = canonical

            # Also check first word match (first name match)
            elif n1_lower.split()[0] == n2_lower.split()[0] and len(n1_lower.split()[0]) > 3:
                # First names match - check if one has institution suffix
                words1 = set(n1_lower.split())
                words2 = set(n2_lower.split())

                # Common institution indicators
                inst_indicators = {'ssn', 'cse', 'ece', 'eee', 'mech', 'bme', 'chem', 'civil',
                                   'g1', 'g2', 'g3', 's1', 's2', 's3', 'a1', 'a2', 'b1', 'b2'}

                has_inst1 = bool(words1 & inst_indicators)
                has_inst2 = bool(words2 & inst_indicators)

                # If one has institution suffix and the other doesn't, they might be same person
                if has_inst1 != has_inst2:
                    # Use the one without institution suffix as canonical
                    if has_inst1:
                        canonical, old = name2, name1
                    else:
                        canonical, old = name1, name2

                    # Only merge if the canonical name words are subset of old name words
                    canonical_words = set(canonical.lower().split())
                    old_words = set(old.lower().split())

                    if canonical_words.issubset(old_words):
                        name_mapping[old] = canonical

    # Apply mapping
    if name_mapping:
        df = df.copy()
        df['sender'] = df['sender'].replace(name_mapping)

        # Log merges for debugging
        for old, new in name_mapping.items():
            print(f"  Merged: '{old}' -> '{new}'")

    return df


def extract_emojis(text):
    """Extract all emojis from text."""
    return [c for c in text if c in emoji.EMOJI_DATA]


def get_basic_stats(df):
    """Get basic chat statistics."""
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
    """Get top message senders."""
    user_df = df[~df['is_system']]
    counts = user_df['sender'].value_counts().head(top_n)
    return counts.to_dict()


def get_hourly_activity(df):
    """Get message distribution by hour."""
    user_df = df[~df['is_system']]
    return user_df['hour'].value_counts().sort_index().to_dict()


def get_daily_activity(df):
    """Get message distribution by day of week."""
    user_df = df[~df['is_system']]
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    counts = user_df['day_of_week'].value_counts()
    return {day: counts.get(day, 0) for day in day_order}


def get_emoji_stats(df, top_n=15):
    """Get most used emojis."""
    user_df = df[~df['is_system']]
    all_emojis = []

    for msg in user_df['message']:
        all_emojis.extend(extract_emojis(str(msg)))

    return dict(Counter(all_emojis).most_common(top_n))


def get_emoji_stats_by_user(df, top_n=5):
    """Get emoji usage by user."""
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

    # Sort by total emoji count
    return dict(sorted(user_emojis.items(), key=lambda x: x[1]['total'], reverse=True)[:top_n])


def get_media_stats(df):
    """Get media sharing statistics."""
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
    """Get most common words (excluding short words, names, and system text)."""
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    # Get participant name parts to filter out
    name_parts = set()
    for sender in user_df['sender'].unique():
        for part in sender.lower().split():
            if len(part) > 2:
                name_parts.add(part)

    words = []
    for msg in user_df['message']:
        # Remove system annotations like "<This message was edited>"
        clean_msg = re.sub(r'<[^>]+>', '', str(msg))
        # Remove @mentions
        clean_msg = re.sub(r'@\S+', '', clean_msg)

        msg_words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_msg.lower())
        words.extend([w for w in msg_words if w not in CHAT_STOP_WORDS and w not in name_parts])

    return dict(Counter(words).most_common(top_n))


def get_conversation_starters(df, gap_minutes=60):
    """Find who starts conversations most often."""
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
    """Find who messages most during late night (12am-5am)."""
    user_df = df[~df['is_system']]
    night_df = user_df[(user_df['hour'] >= 0) & (user_df['hour'] < 5)]

    if night_df.empty:
        return {}

    return night_df['sender'].value_counts().head(5).to_dict()


def get_early_birds(df):
    """Find who messages most during early morning (5am-8am)."""
    user_df = df[~df['is_system']]
    morning_df = user_df[(user_df['hour'] >= 5) & (user_df['hour'] < 8)]

    if morning_df.empty:
        return {}

    return morning_df['sender'].value_counts().head(5).to_dict()


def get_longest_messages(df, top_n=5):
    """Get users with longest average message length."""
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    avg_length = user_df.groupby('sender')['char_count'].mean()
    return avg_length.nlargest(top_n).to_dict()


def get_busiest_dates(df, top_n=5):
    """Get dates with most messages."""
    user_df = df[~df['is_system']]
    return user_df['date'].value_counts().head(top_n).to_dict()


def get_response_pairs(df, window_minutes=5):
    """Find common response pairs (who replies to whom)."""
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
    """Find who sends multiple messages in a row before getting a reply."""
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

    # Don't forget the last streak
    if streak >= 2 and prev_sender:
        double_texts[prev_sender] += streak - 1

    return dict(double_texts.most_common(10))


def get_conversation_killers(df, silence_minutes=30):
    """Find whose messages tend to end conversations."""
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

    # Calculate kill rate
    kill_rates = {}
    for sender, kills in killers.items():
        if total_msgs[sender] > 10:  # Min threshold
            kill_rates[sender] = {
                "kills": kills,
                "total": total_msgs[sender],
                "rate": round(kills / total_msgs[sender] * 100, 1)
            }

    # Sort by kill count
    return dict(sorted(kill_rates.items(), key=lambda x: x[1]['kills'], reverse=True)[:5])


def get_response_times(df):
    """Calculate average response time per person."""
    user_df = df[~df['is_system']].sort_values('datetime').reset_index(drop=True)

    if len(user_df) < 2:
        return {}

    response_times = defaultdict(list)

    for i in range(1, len(user_df)):
        current = user_df.iloc[i]
        prev = user_df.iloc[i - 1]

        # Only count if different sender and within reasonable time
        if current['sender'] != prev['sender']:
            gap_seconds = (current['datetime'] - prev['datetime']).total_seconds()
            # Only count responses within 1 hour
            if 0 < gap_seconds < 3600:
                response_times[current['sender']].append(gap_seconds)

    # Calculate averages
    avg_times = {}
    for sender, times in response_times.items():
        if len(times) >= 5:  # Min threshold
            avg_seconds = sum(times) / len(times)
            avg_times[sender] = {
                "avg_seconds": round(avg_seconds, 1),
                "avg_formatted": format_duration(avg_seconds),
                "response_count": len(times)
            }

    return dict(sorted(avg_times.items(), key=lambda x: x[1]['avg_seconds'])[:10])


def format_duration(seconds):
    """Format seconds into readable duration."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"


def get_caps_users(df):
    """Find who TYPES IN ALL CAPS the most."""
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    caps_count = Counter()
    total_count = Counter()

    for _, row in user_df.iterrows():
        msg = row['message']
        # Only count messages with actual letters
        letters = re.findall(r'[a-zA-Z]', msg)
        if len(letters) >= 5:
            total_count[row['sender']] += 1
            caps_letters = re.findall(r'[A-Z]', msg)
            if len(caps_letters) / len(letters) > 0.7:
                caps_count[row['sender']] += 1

    # Calculate rate
    caps_rates = {}
    for sender, caps in caps_count.items():
        if total_count[sender] > 10:
            caps_rates[sender] = {
                "caps_messages": caps,
                "rate": round(caps / total_count[sender] * 100, 1)
            }

    return dict(sorted(caps_rates.items(), key=lambda x: x[1]['caps_messages'], reverse=True)[:5])


def get_question_askers(df):
    """Find who asks the most questions."""
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    questions = Counter()
    total = Counter()

    for _, row in user_df.iterrows():
        total[row['sender']] += 1
        if '?' in row['message']:
            questions[row['sender']] += 1

    # Calculate rate
    question_stats = {}
    for sender, q_count in questions.items():
        if total[sender] > 10:
            question_stats[sender] = {
                "questions": q_count,
                "rate": round(q_count / total[sender] * 100, 1)
            }

    return dict(sorted(question_stats.items(), key=lambda x: x[1]['questions'], reverse=True)[:5])


def get_link_sharers(df):
    """Find who shares the most links."""
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    url_pattern = r'https?://\S+'
    link_count = Counter()

    for _, row in user_df.iterrows():
        links = re.findall(url_pattern, row['message'])
        if links:
            link_count[row['sender']] += len(links)

    return dict(link_count.most_common(5))


def get_one_worders(df):
    """Find who sends the most one-word messages."""
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    one_word = Counter()
    total = Counter()

    for _, row in user_df.iterrows():
        total[row['sender']] += 1
        words = row['message'].split()
        if len(words) == 1:
            one_word[row['sender']] += 1

    # Calculate rate
    one_word_stats = {}
    for sender, count in one_word.items():
        if total[sender] > 20:
            one_word_stats[sender] = {
                "count": count,
                "rate": round(count / total[sender] * 100, 1)
            }

    return dict(sorted(one_word_stats.items(), key=lambda x: x[1]['rate'], reverse=True)[:5])


def get_laugh_stats(df):
    """Find who laughs (lol, haha, 😂) the most."""
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
    """Calculate the longest daily chat streak."""
    user_df = df[~df['is_system']]

    if user_df.empty:
        return {"longest_streak": 0, "current_streak": 0}

    # Get unique dates
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
    """Find who goes on the longest monologues (consecutive messages)."""
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

    # Final streak
    if streak >= min_streak and prev_sender:
        monologues[prev_sender].append(streak)

    # Summarize
    mono_stats = {}
    for sender, streaks in monologues.items():
        mono_stats[sender] = {
            "longest": max(streaks),
            "total_monologues": len(streaks),
            "avg_length": round(sum(streaks) / len(streaks), 1)
        }

    return dict(sorted(mono_stats.items(), key=lambda x: x[1]['longest'], reverse=True)[:5])


# ============== TF-IDF UNIQUE WORDS ==============

def get_unique_words_per_person(df, top_n=10):
    """
    Find words that are uniquely associated with each person using TF-IDF.
    These are words they use frequently that others don't use much.
    """
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    # Get participant name parts to filter out
    name_parts = set()
    for sender in user_df['sender'].unique():
        for part in sender.lower().split():
            if len(part) > 2:
                name_parts.add(part)

    # Get word counts per person
    person_words = defaultdict(Counter)
    all_words = Counter()

    for _, row in user_df.iterrows():
        # Clean message
        clean_msg = re.sub(r'<[^>]+>', '', str(row['message']))  # Remove <...>
        clean_msg = re.sub(r'@\S+', '', clean_msg)  # Remove @mentions

        words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_msg.lower())
        words = [w for w in words if w not in CHAT_STOP_WORDS and w not in name_parts]
        person_words[row['sender']].update(words)
        all_words.update(words)

    # Calculate TF-IDF style scores
    num_people = len(person_words)
    unique_words = {}

    for sender, words in person_words.items():
        total_words = sum(words.values())
        if total_words < 20:  # Min threshold
            continue

        word_scores = {}
        for word, count in words.items():
            if count < 3:  # Min frequency
                continue

            # TF: frequency in this person's messages
            tf = count / total_words

            # IDF: how unique is this word (inverse of how many people use it)
            people_using = sum(1 for p in person_words.values() if word in p)
            idf = math.log(num_people / people_using) if people_using > 0 else 0

            # Boost words used MUCH more by this person
            personal_rate = count / all_words[word] if all_words[word] > 0 else 0

            score = tf * idf * (1 + personal_rate)
            word_scores[word] = {
                "score": round(score, 4),
                "count": count,
                "exclusivity": round(personal_rate * 100, 1)  # % of usage by this person
            }

        # Sort by score and take top N
        top_words = sorted(word_scores.items(), key=lambda x: x[1]['score'], reverse=True)[:top_n]
        unique_words[sender] = dict(top_words)

    return unique_words


def get_catchphrases(df, min_occurrences=3):
    """Find repeated phrases (2-4 words) unique to each person."""
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    # Get all participant names (lowercased) to filter out mentions
    all_names = set()
    for sender in user_df['sender'].unique():
        # Add full name and individual parts
        name_lower = sender.lower()
        all_names.add(name_lower)
        for part in name_lower.split():
            if len(part) > 2:  # Skip very short parts
                all_names.add(part)

    # Common generic phrases to filter out
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
        # Remove @mentions before processing
        msg = re.sub(r'@\u2068[^⁩]+\u2069', '', str(row['message']))
        msg = msg.lower()
        words = re.findall(r'\b[a-zA-Z]+\b', msg)

        # Extract 2-4 word phrases
        for n in range(2, 5):
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i+n])
                if len(phrase) > 5:  # Min length
                    # Skip generic English phrases
                    if phrase in generic_phrases:
                        continue

                    # Skip phrases that are just names
                    phrase_words = set(phrase.split())
                    name_overlap = phrase_words & all_names
                    if len(name_overlap) >= len(phrase_words) - 1:
                        # Most words are names, skip this phrase
                        continue

                    person_phrases[row['sender']][phrase] += 1
                    all_phrases[phrase] += 1

    # Find phrases unique to each person
    catchphrases = {}
    for sender, phrases in person_phrases.items():
        unique = []
        for phrase, count in phrases.most_common(50):
            if count >= min_occurrences:
                # Check if this person uses it more than 60% of total
                total = all_phrases[phrase]
                if count / total > 0.6:
                    unique.append({
                        "phrase": phrase,
                        "count": count,
                        "exclusivity": round(count / total * 100, 1)
                    })

        if unique:
            catchphrases[sender] = unique[:5]  # Top 5 catchphrases

    return catchphrases


# ============== PERSONALITY TAGS ==============

def assign_personality_tags(df, stats_cache=None):
    """
    Assign personality tags to each person based on their behavior.
    Returns a dict of {person: [list of tags with metadata]}
    """
    user_df = df[~df['is_system']]
    senders = user_df['sender'].unique()

    # Pre-compute stats if not cached
    if stats_cache is None:
        stats_cache = {
            'double_texters': get_double_texters(df),
            'conv_killers': get_conversation_killers(df),
            'response_times': get_response_times(df),
            'caps_users': get_caps_users(df),
            'question_askers': get_question_askers(df),
            'link_sharers': get_link_sharers(df),
            'one_worders': get_one_worders(df),
            'night_owls': get_night_owls(df),
            'early_birds': get_early_birds(df),
            'monologuers': get_monologuers(df),
            'laugh_stats': get_laugh_stats(df),
            'top_chatters': get_top_chatters(df),
            'longest_msgs': get_longest_messages(df),
            'conv_starters': get_conversation_starters(df),
            'media_stats': get_media_stats(df),
            'emoji_stats': get_emoji_stats_by_user(df),
        }

    personality_tags = {}
    total_msgs = len(user_df)

    for sender in senders:
        tags = []
        sender_df = user_df[user_df['sender'] == sender]
        msg_count = len(sender_df)

        if msg_count < 5:  # Skip inactive users
            continue

        msg_share = msg_count / total_msgs * 100

        # === ACTIVITY TAGS ===
        if sender in stats_cache['top_chatters']:
            rank = list(stats_cache['top_chatters'].keys()).index(sender) + 1
            if rank == 1:
                tags.append({"tag": "chatterbox", "detail": f"#{rank} with {msg_count} messages", "icon": ""})
            elif rank <= 3:
                tags.append({"tag": "active_member", "detail": f"#{rank} most active", "icon": ""})

        if msg_share < 5 and msg_count > 10:
            tags.append({"tag": "lurker", "detail": f"Only {msg_share:.1f}% of messages", "icon": ""})

        # === TIMING TAGS ===
        if sender in stats_cache['night_owls']:
            night_count = stats_cache['night_owls'][sender]
            if night_count > 20:
                tags.append({"tag": "night_owl", "detail": f"{night_count} late night msgs", "icon": ""})

        if sender in stats_cache['early_birds']:
            morning_count = stats_cache['early_birds'][sender]
            if morning_count > 10:
                tags.append({"tag": "early_bird", "detail": f"{morning_count} early msgs", "icon": ""})

        # === CONVERSATION TAGS ===
        if sender in stats_cache['conv_starters']:
            starts = stats_cache['conv_starters'][sender]
            if starts > 10:
                tags.append({"tag": "conversation_starter", "detail": f"Started {starts} convos", "icon": ""})

        if sender in stats_cache['conv_killers']:
            kills = stats_cache['conv_killers'][sender]['kills']
            rate = stats_cache['conv_killers'][sender]['rate']
            if kills > 5 and rate > 10:
                tags.append({"tag": "conversation_killer", "detail": f"{rate}% kill rate", "icon": ""})

        # === RESPONSE TAGS ===
        if sender in stats_cache['response_times']:
            avg_time = stats_cache['response_times'][sender]['avg_seconds']
            if avg_time < 30:
                tags.append({"tag": "speed_demon", "detail": f"Avg {int(avg_time)}s response", "icon": ""})
            elif avg_time > 300:
                tags.append({"tag": "ghost", "detail": f"Avg {int(avg_time//60)}min response", "icon": ""})

        if sender in stats_cache['double_texters']:
            double_count = stats_cache['double_texters'][sender]
            if double_count > 20:
                tags.append({"tag": "double_texter", "detail": f"{double_count} double texts", "icon": ""})

        # === STYLE TAGS ===
        if sender in stats_cache['longest_msgs']:
            avg_len = stats_cache['longest_msgs'][sender]
            if avg_len > 100:
                tags.append({"tag": "essay_writer", "detail": f"~{int(avg_len)} chars avg", "icon": ""})

        if sender in stats_cache['one_worders']:
            rate = stats_cache['one_worders'][sender]['rate']
            if rate > 30:
                tags.append({"tag": "one_worder", "detail": f"{rate}% one-word msgs", "icon": ""})

        if sender in stats_cache['caps_users']:
            caps_data = stats_cache['caps_users'][sender]
            if caps_data['caps_messages'] > 10:
                tags.append({"tag": "caps_lock", "detail": f"{caps_data['caps_messages']} SHOUTY msgs", "icon": ""})

        # === CONTENT TAGS ===
        if sender in stats_cache['question_askers']:
            q_data = stats_cache['question_askers'][sender]
            if q_data['questions'] > 20:
                tags.append({"tag": "question_asker", "detail": f"{q_data['questions']} questions", "icon": ""})

        if sender in stats_cache['link_sharers']:
            links = stats_cache['link_sharers'][sender]
            if links > 10:
                tags.append({"tag": "link_dropper", "detail": f"{links} links shared", "icon": ""})

        if sender in stats_cache['monologuers']:
            mono = stats_cache['monologuers'][sender]
            if mono['longest'] > 8:
                tags.append({"tag": "monologuer", "detail": f"Longest streak: {mono['longest']}", "icon": ""})

        if sender in stats_cache['laugh_stats']:
            laughs = stats_cache['laugh_stats'][sender]
            if laughs > 30:
                tags.append({"tag": "lol_addict", "detail": f"{laughs} laughs", "icon": ""})

        # === MEDIA TAGS ===
        if 'top_sharers' in stats_cache['media_stats']:
            if sender in stats_cache['media_stats']['top_sharers']:
                media_count = stats_cache['media_stats']['top_sharers'][sender]
                if media_count > 20:
                    tags.append({"tag": "media_king", "detail": f"{media_count} media shared", "icon": ""})

        # === EMOJI TAGS ===
        if sender in stats_cache['emoji_stats']:
            emoji_count = stats_cache['emoji_stats'][sender]['total']
            if emoji_count > 50:
                tags.append({"tag": "emoji_spammer", "detail": f"{emoji_count} emojis used", "icon": ""})

        if tags:
            personality_tags[sender] = tags

    return personality_tags


# ============== ROAST TEMPLATES ==============

ROAST_TEMPLATES = {
    "chatterbox": [
        "treats this group like their personal diary",
        "has no one else to talk to apparently",
        "would text a wall if it had WhatsApp",
    ],
    "lurker": [
        "watches from the shadows like a WhatsApp ghost",
        "contributes less than a read receipt",
        "is basically a security camera for this chat",
    ],
    "night_owl": [
        "sleeps when the sun is up like a caffeinated vampire",
        "probably types under their blanket at 3am",
        "thinks 2am is a reasonable time for 'quick question'",
    ],
    "early_bird": [
        "sends good morning texts before the birds wake up",
        "is aggressively cheerful at ungodly hours",
        "thinks dawn is prime texting time",
    ],
    "conversation_starter": [
        "can't stand silence, even digital silence",
        "starts conversations like they're getting paid per chat",
        "is allergic to an inactive group",
    ],
    "conversation_killer": [
        "has the superpower of ending any conversation",
        "makes crickets jealous with their chat-killing ability",
        "should come with a 'conversation may end' warning",
    ],
    "speed_demon": [
        "replies faster than autocorrect can mess up",
        "has WhatsApp surgically attached to their fingers",
        "makes instant replies look slow",
    ],
    "ghost": [
        "takes longer to reply than a government office",
        "treats 'seen' as a final response",
        "is online but spiritually elsewhere",
    ],
    "double_texter": [
        "sends messages like they're being charged per conversation",
        "thinks one message is never enough",
        "has separation anxiety from the send button",
    ],
    "essay_writer": [
        "writes texts that need a table of contents",
        "treats WhatsApp like a dissertation platform",
        "makes emails look concise",
    ],
    "one_worder": [
        "communicates exclusively in grunts and 'ok'",
        "makes fortune cookies look verbose",
        "treats words like they cost money",
    ],
    "caps_lock": [
        "DOESN'T KNOW WHAT INSIDE VOICE MEANS",
        "types like they're perpetually excited or angry",
        "makes every message feel like an emergency",
    ],
    "question_asker": [
        "treats this chat like a search engine",
        "asks more questions than a 5-year-old",
        "should be sponsored by Question Mark Inc.",
    ],
    "link_dropper": [
        "thinks every conversation needs a source citation",
        "is basically a human RSS feed",
        "has never had an original thought, just links",
    ],
    "monologuer": [
        "doesn't need replies, just an audience",
        "holds conversations with themselves professionally",
        "treats group chat as a podcast platform",
    ],
    "lol_addict": [
        "laughs at everything including grocery lists",
        "uses 😂 as punctuation",
        "finds literally everything hilarious apparently",
    ],
    "media_king": [
        "has a meme for every occasion",
        "treats chat storage as a personal challenge",
        "communicates primarily through images",
    ],
    "emoji_spammer": [
        "uses more emojis than actual words",
        "thinks text without emojis is just sad",
        "has evolved beyond human language",
    ],
}


def generate_roast(person, tags, unique_words, catchphrases):
    """Generate a roast for a person based on their tags and unique words."""
    import random

    if not tags:
        return None

    roast_parts = []

    # Pick 2-3 tags to roast
    selected_tags = tags[:min(3, len(tags))]

    for tag_info in selected_tags:
        tag = tag_info['tag']
        if tag in ROAST_TEMPLATES:
            template = random.choice(ROAST_TEMPLATES[tag])
            roast_parts.append(template)

    # Add unique word mention if available
    if person in unique_words and unique_words[person]:
        top_word = list(unique_words[person].keys())[0]
        roast_parts.append(f"won't stop saying '{top_word}'")

    # Add catchphrase if available
    if person in catchphrases and catchphrases[person]:
        phrase = catchphrases[person][0]['phrase']
        roast_parts.append(f"(trademark phrase: '{phrase}')")

    if not roast_parts:
        return None

    # Assemble roast
    name = person.split()[0]  # First name only
    roast = f"{name} {roast_parts[0]}"
    if len(roast_parts) > 1:
        roast += f", {roast_parts[1]}"
    if len(roast_parts) > 2:
        roast += f". {roast_parts[2].capitalize()}"

    return roast


# ============== GROUP VIBE / TOPICS ==============

def get_interesting_topics(df, top_n=15):
    """
    Find interesting group topics - proper nouns, unique terms, recurring themes.
    Not just common words, but things the group actually talks about.
    """
    user_df = df[(~df['is_system']) & (df['media_type'].isna())]

    # Get participant name parts to filter out
    name_parts = set()
    for sender in user_df['sender'].unique():
        for part in sender.lower().split():
            if len(part) > 2:
                name_parts.add(part)

    # Count words, but also track if they appear capitalized (proper nouns)
    word_counts = Counter()
    proper_noun_bonus = Counter()

    for _, row in user_df.iterrows():
        # Clean message
        clean_msg = re.sub(r'<[^>]+>', '', str(row['message']))
        clean_msg = re.sub(r'@\S+', '', clean_msg)

        # Find capitalized words (potential proper nouns)
        caps_words = set(re.findall(r'\b[A-Z][a-z]{2,}\b', clean_msg))

        # Get all words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', clean_msg.lower())
        for w in words:
            if w not in TOPIC_ONLY_STOP_WORDS and w not in name_parts:
                word_counts[w] += 1
                # Bonus for words that appear capitalized (proper nouns)
                if w.capitalize() in caps_words:
                    proper_noun_bonus[w] += 0.5

    # Score words: frequency + proper noun bonus
    scored_words = {}
    for word, count in word_counts.items():
        if count >= 3:  # Min frequency
            score = count + proper_noun_bonus.get(word, 0)
            scored_words[word] = {"count": count, "score": score}

    # Sort by score and return top N
    sorted_topics = sorted(scored_words.items(), key=lambda x: x[1]['score'], reverse=True)
    return [word for word, _ in sorted_topics[:top_n]]


def get_group_vibe(df, emoji_stats, hourly_activity):
    """Determine the overall vibe/personality of the group."""
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

    # Determine energy level
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

    # Determine peak activity time
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

    # Extract INTERESTING topics (not generic words)
    vibe["topics"] = get_interesting_topics(df)

    # Check emoji vibe
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

    # Generate description
    personality_str = ", ".join(vibe["personality"][:3])
    topics_str = ", ".join(vibe["topics"][:5]) if vibe["topics"] else "everything and nothing"

    vibe["description"] = f"A {vibe['energy']} energy group of {personality_str} folks who mostly talk about {topics_str}."

    return vibe


# ============== LLM CONTEXT PREPARATION ==============

def prepare_llm_context(df, max_sample_messages=50):
    """
    Prepare a condensed context for LLM analysis.
    This extracts all the intelligence locally, so the LLM just needs to be creative.
    """
    user_df = df[~df['is_system']]

    # Get all stats
    basic_stats = get_basic_stats(df)
    word_stats = get_word_stats(df)
    emoji_stats = get_emoji_stats(df)
    hourly = get_hourly_activity(df)

    # Pre-compute stats for tag assignment
    stats_cache = {
        'double_texters': get_double_texters(df),
        'conv_killers': get_conversation_killers(df),
        'response_times': get_response_times(df),
        'caps_users': get_caps_users(df),
        'question_askers': get_question_askers(df),
        'link_sharers': get_link_sharers(df),
        'one_worders': get_one_worders(df),
        'night_owls': get_night_owls(df),
        'early_birds': get_early_birds(df),
        'monologuers': get_monologuers(df),
        'laugh_stats': get_laugh_stats(df),
        'top_chatters': get_top_chatters(df),
        'longest_msgs': get_longest_messages(df),
        'conv_starters': get_conversation_starters(df),
        'media_stats': get_media_stats(df),
        'emoji_stats': get_emoji_stats_by_user(df),
    }

    # Get derived insights
    personality_tags = assign_personality_tags(df, stats_cache)
    unique_words = get_unique_words_per_person(df)
    catchphrases = get_catchphrases(df)
    group_vibe = get_group_vibe(df, emoji_stats, hourly)

    # Sample interesting messages (varied by person and content)
    sample_messages = []
    text_df = user_df[(user_df['media_type'].isna()) & (user_df['char_count'] > 10)]

    if not text_df.empty:
        # Sample proportionally from each person
        for sender in text_df['sender'].unique():
            sender_msgs = text_df[text_df['sender'] == sender]
            n_sample = min(max_sample_messages // len(text_df['sender'].unique()), len(sender_msgs))
            if n_sample > 0:
                sampled = sender_msgs.sample(n=min(n_sample, len(sender_msgs)))
                for _, row in sampled.iterrows():
                    sample_messages.append({
                        "sender": row['sender'],
                        "message": row['message'][:200],  # Truncate long messages
                        "hour": row['hour']
                    })

    # Build per-person profiles
    person_profiles = {}
    for sender in user_df['sender'].unique():
        sender_df = user_df[user_df['sender'] == sender]
        if len(sender_df) < 5:
            continue

        profile = {
            "message_count": len(sender_df),
            "message_share": round(len(sender_df) / len(user_df) * 100, 1),
        }

        # Add tags
        if sender in personality_tags:
            profile["tags"] = [t["tag"] for t in personality_tags[sender]]

        # Add unique words
        if sender in unique_words:
            profile["signature_words"] = list(unique_words[sender].keys())[:5]

        # Add catchphrases
        if sender in catchphrases:
            profile["catchphrases"] = [p["phrase"] for p in catchphrases[sender][:3]]

        # Add top emojis
        if sender in stats_cache['emoji_stats']:
            profile["top_emojis"] = list(stats_cache['emoji_stats'][sender]['top'].keys())

        person_profiles[sender] = profile

    # Build final context
    context = {
        "group_overview": {
            "total_messages": basic_stats["total_messages"] if basic_stats else 0,
            "participants": list(person_profiles.keys()),
            "date_range": f"{basic_stats['first_message'].strftime('%Y-%m-%d')} to {basic_stats['last_message'].strftime('%Y-%m-%d')}" if basic_stats else "",
            "vibe": group_vibe,
        },
        "top_topics": get_interesting_topics(df)[:15],
        "top_emojis": list(emoji_stats.keys())[:10] if emoji_stats else [],
        "person_profiles": person_profiles,
        "sample_messages": sample_messages[:max_sample_messages],
    }

    return context, personality_tags, unique_words, catchphrases, group_vibe


# ============== DISPLAY FUNCTIONS ==============

def display_header(basic_stats, group_name=None):
    """Display the wrapped header."""
    console.print()

    if group_name:
        header_text = (
            f"[bold magenta]WhatsApp Wrapped 2025[/bold magenta]\n"
            f"[cyan]{group_name}[/cyan]\n"
            f"[dim]Your year in messages[/dim]"
        )
    else:
        header_text = (
            "[bold magenta]WhatsApp Wrapped 2025[/bold magenta]\n"
            "[dim]Your year in messages[/dim]"
        )

    console.print(Panel.fit(
        header_text,
        border_style="magenta",
        padding=(1, 4)
    ))
    console.print()


def display_basic_stats(stats):
    """Display basic statistics."""
    if not stats:
        console.print("[red]No messages found![/red]")
        return

    console.print(Panel(
        f"[cyan]{stats['total_messages']:,}[/cyan] messages from "
        f"[cyan]{stats['total_participants']}[/cyan] people\n"
        f"[cyan]{stats['total_words']:,}[/cyan] words written over "
        f"[cyan]{stats['date_range_days']}[/cyan] days\n\n"
        f"[dim]First message:[/dim] {stats['first_message'].strftime('%b %d, %Y %I:%M %p')}\n"
        f"[dim]Last message:[/dim] {stats['last_message'].strftime('%b %d, %Y %I:%M %p')}",
        title="Overview",
        border_style="blue"
    ))
    console.print()


def display_top_chatters(chatters):
    """Display top message senders."""
    if not chatters:
        return

    table = Table(title="Top Chatters", box=box.ROUNDED, border_style="green")
    table.add_column("Rank", style="dim", width=4)
    table.add_column("Member", style="cyan")
    table.add_column("Messages", justify="right", style="green")
    table.add_column("", width=20)  # Bar chart

    max_count = max(chatters.values())

    medals = ["", "", "", "", "", "", "", "", "", ""]
    for i, (member, count) in enumerate(chatters.items()):
        bar_length = int((count / max_count) * 15)
        bar = "" * bar_length
        table.add_row(
            medals[i] if i < len(medals) else str(i + 1),
            member,
            f"{count:,}",
            f"[green]{bar}[/green]"
        )

    console.print(table)
    console.print()


def display_hourly_activity(hourly):
    """Display hourly activity chart."""
    if not hourly:
        return

    console.print(Panel("[bold]When You're Most Active[/bold]", border_style="yellow"))

    max_count = max(hourly.values()) if hourly else 1

    # Create hour labels
    for hour in range(24):
        count = hourly.get(hour, 0)
        bar_length = int((count / max_count) * 30) if max_count > 0 else 0
        bar = "" * bar_length

        # Color based on time of day
        if 0 <= hour < 6:
            color = "blue"  # Night
            period = ""
        elif 6 <= hour < 12:
            color = "yellow"  # Morning
            period = ""
        elif 12 <= hour < 18:
            color = "green"  # Afternoon
            period = ""
        else:
            color = "magenta"  # Evening
            period = ""

        time_label = f"{hour:02d}:00"
        console.print(f"  {period} {time_label} [{color}]{bar}[/{color}] {count}")

    console.print()


def display_daily_activity(daily):
    """Display daily activity."""
    if not daily:
        return

    table = Table(title="Messages by Day", box=box.ROUNDED, border_style="cyan")
    table.add_column("Day", style="cyan")
    table.add_column("Messages", justify="right")
    table.add_column("", width=25)

    max_count = max(daily.values()) if daily else 1

    for day, count in daily.items():
        bar_length = int((count / max_count) * 20) if max_count > 0 else 0
        bar = "" * bar_length
        table.add_row(day[:3], f"{count:,}", f"[cyan]{bar}[/cyan]")

    console.print(table)
    console.print()


def display_emoji_stats(emojis, user_emojis):
    """Display emoji statistics."""
    if not emojis:
        console.print("[dim]No emojis found[/dim]")
        return

    # Top emojis panel
    emoji_str = "  ".join([f"{e} ({c})" for e, c in list(emojis.items())[:10]])
    console.print(Panel(
        f"[bold]Most Used Emojis[/bold]\n\n{emoji_str}",
        border_style="yellow"
    ))

    # User emoji table
    if user_emojis:
        table = Table(title="Emoji Champions", box=box.ROUNDED, border_style="yellow")
        table.add_column("Member", style="cyan")
        table.add_column("Total", justify="right")
        table.add_column("Favorites")

        for user, data in user_emojis.items():
            faves = " ".join(data['top'].keys())
            table.add_row(user, str(data['total']), faves)

        console.print(table)

    console.print()


def display_media_stats(media):
    """Display media sharing stats."""
    if media.get('total', 0) == 0:
        return

    table = Table(title="Media Shared", box=box.ROUNDED, border_style="magenta")
    table.add_column("Type", style="cyan")
    table.add_column("Count", justify="right", style="green")

    icons = {
        "image": "",
        "video": "",
        "sticker": "",
        "audio": "",
        "gif": "",
        "document": "",
        "contact": "",
        "location": ""
    }

    for media_type, count in media.get('by_type', {}).items():
        icon = icons.get(media_type, "")
        table.add_row(f"{icon} {media_type.title()}", str(count))

    console.print(table)

    if media.get('top_sharers'):
        console.print()
        table2 = Table(title="Top Media Sharers", box=box.ROUNDED, border_style="magenta")
        table2.add_column("Member", style="cyan")
        table2.add_column("Media Shared", justify="right")

        for user, count in media['top_sharers'].items():
            table2.add_row(user, str(count))

        console.print(table2)

    console.print()


def display_word_stats(words):
    """Display common words."""
    if not words:
        return

    # Create word cloud-like display
    word_list = []
    max_count = max(words.values())

    for word, count in words.items():
        # Size based on frequency
        if count > max_count * 0.7:
            word_list.append(f"[bold cyan]{word}[/bold cyan]")
        elif count > max_count * 0.4:
            word_list.append(f"[cyan]{word}[/cyan]")
        else:
            word_list.append(f"[dim]{word}[/dim]")

    console.print(Panel(
        "  ".join(word_list),
        title="Most Used Words",
        border_style="blue"
    ))
    console.print()


def display_special_stats(starters, night_owls, early_birds, longest_msgs):
    """Display special personality-based stats."""

    # Conversation starters
    if starters:
        starter_list = list(starters.items())[:3]
        starter_text = "\n".join([f"  {i+1}. {name} ({count} times)"
                                   for i, (name, count) in enumerate(starter_list)])
        console.print(Panel(
            f"[bold]Conversation Starters[/bold]\n{starter_text}",
            border_style="green"
        ))

    # Night owls and early birds
    if night_owls or early_birds:
        cols = []

        if night_owls:
            owl_text = "\n".join([f"  {name}: {count}" for name, count in list(night_owls.items())[:3]])
            cols.append(f"[bold] Night Owls[/bold]\n[dim](12am-5am)[/dim]\n{owl_text}")

        if early_birds:
            bird_text = "\n".join([f"  {name}: {count}" for name, count in list(early_birds.items())[:3]])
            cols.append(f"[bold] Early Birds[/bold]\n[dim](5am-8am)[/dim]\n{bird_text}")

        console.print(Panel("\n\n".join(cols), border_style="blue"))

    # Longest messages
    if longest_msgs:
        long_text = "\n".join([f"  {name}: ~{int(length)} chars avg"
                               for name, length in list(longest_msgs.items())[:3]])
        console.print(Panel(
            f"[bold] Essay Writers[/bold]\n[dim](Longest avg messages)[/dim]\n{long_text}",
            border_style="cyan"
        ))

    console.print()


def display_busiest_dates(dates):
    """Display busiest chat dates."""
    if not dates:
        return

    table = Table(title="Busiest Days", box=box.ROUNDED, border_style="red")
    table.add_column("Date", style="cyan")
    table.add_column("Messages", justify="right", style="green")

    for date, count in dates.items():
        table.add_row(date.strftime('%B %d, %Y'), str(count))

    console.print(table)
    console.print()


def display_response_pairs(pairs):
    """Display common response pairs."""
    if not pairs:
        return

    table = Table(title="Chat Dynamics (Who Replies to Whom)", box=box.ROUNDED, border_style="cyan")
    table.add_column("Sender", style="cyan")
    table.add_column("", width=3)
    table.add_column("Replier", style="green")
    table.add_column("Times", justify="right")

    for (sender, replier), count in list(pairs.items())[:7]:
        # Truncate long names
        s_name = sender[:15] + "..." if len(sender) > 15 else sender
        r_name = replier[:15] + "..." if len(replier) > 15 else replier
        table.add_row(s_name, "", r_name, str(count))

    console.print(table)
    console.print()


def display_response_times(response_times):
    """Display response time stats."""
    if not response_times:
        return

    table = Table(title="Response Time Leaderboard", box=box.ROUNDED, border_style="green")
    table.add_column("Member", style="cyan")
    table.add_column("Avg Response", justify="right")
    table.add_column("Speed", width=15)

    for i, (sender, data) in enumerate(response_times.items()):
        avg = data['avg_seconds']
        if avg < 30:
            speed = "[green]" + "" * 5 + "[/green]"
        elif avg < 60:
            speed = "[green]" + "" * 4 + "[/green]"
        elif avg < 120:
            speed = "[yellow]" + "" * 3 + "[/yellow]"
        elif avg < 300:
            speed = "[yellow]" + "" * 2 + "[/yellow]"
        else:
            speed = "[red]" + "" + "[/red]"

        name = sender[:20] + "..." if len(sender) > 20 else sender
        table.add_row(name, data['avg_formatted'], speed)

        if i >= 6:
            break

    console.print(table)
    console.print()


def display_personality_tags(personality_tags):
    """Display personality tags for each person."""
    if not personality_tags:
        return

    console.print(Panel("[bold]Personality Profiles[/bold]", border_style="magenta"))

    for sender, tags in list(personality_tags.items())[:8]:
        name = sender.split()[0]  # First name
        tag_strs = [f"{t['icon']} {t['tag'].replace('_', ' ')}" for t in tags[:4]]
        console.print(f"  [cyan]{name}[/cyan]: {' | '.join(tag_strs)}")

    console.print()


def display_unique_words(unique_words):
    """Display unique signature words per person."""
    if not unique_words:
        return

    table = Table(title="Signature Words (TF-IDF)", box=box.ROUNDED, border_style="blue")
    table.add_column("Member", style="cyan")
    table.add_column("Their Words", style="dim")

    for sender, words in list(unique_words.items())[:6]:
        name = sender[:15] + "..." if len(sender) > 15 else sender
        word_list = list(words.keys())[:5]
        table.add_row(name, ", ".join(word_list))

    console.print(table)
    console.print()


def display_catchphrases(catchphrases):
    """Display catchphrases per person."""
    if not catchphrases:
        return

    console.print(Panel("[bold]Catchphrases[/bold]", border_style="yellow"))

    for sender, phrases in list(catchphrases.items())[:5]:
        name = sender.split()[0]
        top_phrase = phrases[0]['phrase'] if phrases else None
        if top_phrase:
            console.print(f"  [cyan]{name}[/cyan]: \"{top_phrase}\" ({phrases[0]['count']}x)")

    console.print()


def display_group_vibe(vibe):
    """Display the group's overall vibe."""
    if not vibe or not vibe.get('description'):
        return

    personality = ", ".join(vibe.get('personality', [])[:4])
    topics = ", ".join(vibe.get('topics', [])[:6])

    content = f"[bold]Energy:[/bold] {vibe.get('energy', 'unknown').upper()}\n"
    content += f"[bold]Personality:[/bold] {personality}\n"
    content += f"[bold]Peak Time:[/bold] {vibe.get('peak_time', 'unknown')}\n"
    content += f"[bold]Hot Topics:[/bold] {topics}\n\n"
    content += f"[dim italic]{vibe.get('description', '')}[/dim italic]"

    console.print(Panel(content, title="Group Vibe", border_style="magenta"))
    console.print()


def display_roasts(personality_tags, unique_words, catchphrases):
    """Display generated roasts for each person."""
    if not personality_tags:
        return

    console.print(Panel("[bold red]The Roast Section[/bold red]", border_style="red"))

    for sender, tags in personality_tags.items():
        roast = generate_roast(sender, tags, unique_words, catchphrases)
        if roast:
            console.print(f"  [yellow]{roast}[/yellow]")

    console.print()


def display_streak_stats(streak_stats):
    """Display chat streak statistics."""
    if not streak_stats or streak_stats.get('longest_streak', 0) == 0:
        return

    console.print(Panel(
        f"[bold]Longest Streak:[/bold] {streak_stats['longest_streak']} days\n"
        f"[bold]Active Days:[/bold] {streak_stats.get('total_active_days', 0)} days",
        title="Chat Streak",
        border_style="green"
    ))
    console.print()


def display_double_texters(double_texters):
    """Display double-texter stats."""
    if not double_texters:
        return

    items = list(double_texters.items())[:5]
    text = "\n".join([f"  {name.split()[0]}: {count} times" for name, count in items])

    console.print(Panel(
        f"[bold]Double Texters[/bold]\n[dim](Messages before getting a reply)[/dim]\n{text}",
        border_style="yellow"
    ))
    console.print()


def display_conversation_killers(killers):
    """Display conversation killer stats."""
    if not killers:
        return

    items = list(killers.items())[:5]
    text = "\n".join([
        f"  {name.split()[0]}: {data['kills']} kills ({data['rate']}%)"
        for name, data in items
    ])

    console.print(Panel(
        f"[bold]Conversation Killers[/bold]\n[dim](Messages that end the chat)[/dim]\n{text}",
        border_style="red"
    ))
    console.print()


def display_llm_context(context):
    """Display what would be sent to the LLM (for debugging)."""
    console.print(Panel("[bold]LLM Context Preview[/bold]", border_style="dim"))
    console.print(f"[dim]Context size: ~{len(json.dumps(context))} chars[/dim]")
    console.print(f"[dim]Participants: {len(context.get('person_profiles', {}))}[/dim]")
    console.print(f"[dim]Sample messages: {len(context.get('sample_messages', []))}[/dim]")
    console.print()


def run_wrapped(file_path, show_llm_context=False):
    """Run the full WhatsApp Wrapped analysis."""
    console.print(f"\n[dim]Loading chat from {file_path}...[/dim]\n")

    try:
        df = parse_whatsapp(file_path)
    except FileNotFoundError:
        console.print(f"[red]Error: File '{file_path}' not found![/red]")
        return
    except Exception as e:
        console.print(f"[red]Error parsing file: {e}[/red]")
        return

    if df.empty:
        console.print("[red]No messages found in the file![/red]")
        return

    # Merge renamed contacts first (e.g., "Sanjjit S CSE G2 SSN" -> "Sanjjit S")
    df = merge_similar_contacts(df)

    # Then detect and filter group names (appear as "senders" in system messages)
    df, group_names, current_group_name = detect_group_names(df)

    console.print("[dim]Analyzing chat patterns...[/dim]\n")

    # === BASIC STATS ===
    basic_stats = get_basic_stats(df)
    top_chatters = get_top_chatters(df)
    hourly = get_hourly_activity(df)
    daily = get_daily_activity(df)
    emojis = get_emoji_stats(df)
    user_emojis = get_emoji_stats_by_user(df)
    media = get_media_stats(df)
    words = get_word_stats(df)
    starters = get_conversation_starters(df)
    night_owls = get_night_owls(df)
    early_birds = get_early_birds(df)
    longest_msgs = get_longest_messages(df)
    busiest_dates = get_busiest_dates(df)
    response_pairs = get_response_pairs(df)

    # === NEW BEHAVIORAL STATS ===
    double_texters = get_double_texters(df)
    conv_killers = get_conversation_killers(df)
    response_times = get_response_times(df)
    streak_stats = get_streak_stats(df)

    # === PERSONALITY & ROASTS ===
    unique_words = get_unique_words_per_person(df)
    catchphrases = get_catchphrases(df)

    # Build stats cache for personality tags
    stats_cache = {
        'double_texters': double_texters,
        'conv_killers': conv_killers,
        'response_times': response_times,
        'caps_users': get_caps_users(df),
        'question_askers': get_question_askers(df),
        'link_sharers': get_link_sharers(df),
        'one_worders': get_one_worders(df),
        'night_owls': night_owls,
        'early_birds': early_birds,
        'monologuers': get_monologuers(df),
        'laugh_stats': get_laugh_stats(df),
        'top_chatters': top_chatters,
        'longest_msgs': longest_msgs,
        'conv_starters': starters,
        'media_stats': media,
        'emoji_stats': user_emojis,
    }

    personality_tags = assign_personality_tags(df, stats_cache)
    group_vibe = get_group_vibe(df, emojis, hourly)

    # === DISPLAY EVERYTHING ===
    display_header(basic_stats, current_group_name)
    display_basic_stats(basic_stats)
    display_group_vibe(group_vibe)
    display_top_chatters(top_chatters)
    display_streak_stats(streak_stats)
    display_hourly_activity(hourly)
    display_daily_activity(daily)
    display_response_times(response_times)
    display_emoji_stats(emojis, user_emojis)
    display_media_stats(media)
    display_word_stats(words)
    display_unique_words(unique_words)
    display_catchphrases(catchphrases)
    display_special_stats(starters, night_owls, early_birds, longest_msgs)
    display_double_texters(double_texters)
    display_conversation_killers(conv_killers)
    display_busiest_dates(busiest_dates)
    display_response_pairs(response_pairs)
    display_personality_tags(personality_tags)
    display_roasts(personality_tags, unique_words, catchphrases)

    # === LLM CONTEXT (for future AI integration) ===
    if show_llm_context:
        llm_context, _, _, _, _ = prepare_llm_context(df)
        display_llm_context(llm_context)

        # Save context to file for inspection
        with open("llm_context.json", "w") as f:
            json.dump(llm_context, f, indent=2, default=str)
        console.print("[dim]LLM context saved to llm_context.json[/dim]\n")

    # Final message
    console.print(Panel.fit(
        "[bold green]That's a wrap![/bold green]\n"
        "[dim]Thanks for the memories[/dim]",
        border_style="green",
        padding=(1, 4)
    ))


if __name__ == "__main__":
    import sys

    file_path = "chat.txt"
    show_llm = False

    for arg in sys.argv[1:]:
        if arg == "--llm-context":
            show_llm = True
        elif not arg.startswith("-"):
            file_path = arg

    run_wrapped(file_path, show_llm_context=show_llm)
