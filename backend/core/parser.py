# parser - wa chat parsing and preprocessing

import re
import pandas as pd
from datetime import datetime
import emoji

from .constants import SYSTEM_PATTERNS, IGNORED_SENDERS, MEDIA_PATTERNS


def _parse_datetime(date_str, time_str):
    """Parse date and time strings in various WhatsApp formats"""
    # Date formats to try
    date_formats = ['%d/%m/%y', '%m/%d/%y', '%d/%m/%Y', '%m/%d/%Y']
    # Time formats to try
    time_formats = ['%I:%M:%S %p', '%I:%M %p', '%H:%M:%S', '%H:%M']

    msg_date = None
    for fmt in date_formats:
        try:
            msg_date = datetime.strptime(date_str, fmt)
            break
        except ValueError:
            continue

    if msg_date is None:
        return None, None

    msg_time = None
    for fmt in time_formats:
        try:
            msg_time = datetime.strptime(time_str.strip(), fmt)
            break
        except ValueError:
            continue

    if msg_time is None:
        return None, None

    return msg_date, msg_time


def _parse_lines(lines):
    """Internal parser that works on an iterable of lines"""
    # Multiple patterns to handle different WhatsApp export formats
    patterns = [
        # [DD/MM/YY, H:MM:SS AM/PM] Sender: Message (iOS format)
        r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}(?::\d{2})?\s?[APap][Mm])\]\s([^:]+):\s(.*)$',
        # [DD/MM/YY, HH:MM:SS] Sender: Message (24-hour format)
        r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}(?::\d{2})?)\]\s([^:]+):\s(.*)$',
        # DD/MM/YY, H:MM AM/PM - Sender: Message (Android format without brackets)
        r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}(?::\d{2})?\s?[APap][Mm])\s[-–]\s([^:]+):\s(.*)$',
        # DD/MM/YY, HH:MM - Sender: Message (Android 24-hour without brackets)
        r'^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}(?::\d{2})?)\s[-–]\s([^:]+):\s(.*)$',
    ]

    data = []
    current_message = None

    for line in lines:
        # strip ltr mark
        line = line.replace('\u200e', '').strip()

        if not line:
            continue

        match = None
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                break

        if match:
            if current_message:
                data.append(current_message)

            date_str, time_str, sender, content = match.groups()

            msg_date, msg_time = _parse_datetime(date_str, time_str)
            if msg_date is None or msg_time is None:
                # Couldn't parse, treat as continuation
                if current_message:
                    current_message["message"] += "\n" + line
                    current_message["word_count"] += len(line.split())
                    current_message["char_count"] += len(line)
                continue

            full_datetime = msg_date.replace(
                hour=msg_time.hour,
                minute=msg_time.minute,
                second=msg_time.second
            )

            is_system = any(p in content for p in SYSTEM_PATTERNS) or sender.strip() in IGNORED_SENDERS

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
            # multiline continuation
            if current_message:
                current_message["message"] += "\n" + line
                current_message["word_count"] += len(line.split())
                current_message["char_count"] += len(line)

    if current_message:
        data.append(current_message)

    return pd.DataFrame(data)


def parse_whatsapp(file_path):
    """Parse WhatsApp export from file path (for CLI)"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return _parse_lines(f)


def parse_whatsapp_content(content: str):
    """Parse WhatsApp export from string content (for API)"""
    return _parse_lines(content.split('\n'))


def detect_group_names(df):
    # group names show up as "senders" for system msgs like "you created group" etc
    if df.empty:
        return df, set(), None

    # patterns where group name is the sender
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

    for sender in df['sender'].unique():
        sender_df = df[df['sender'] == sender]

        # if ALL msgs from sender are system msgs, it's a group name
        all_system = True
        for _, row in sender_df.iterrows():
            msg = str(row['message'])
            is_system_msg = any(pattern.lower() in msg.lower() for pattern in group_system_patterns)
            if not is_system_msg and not row['is_system']:
                all_system = False
                break

        if all_system and len(sender_df) > 0:
            group_names.add(sender)

            # extract group name from rename msgs
            for _, row in sender_df.iterrows():
                msg = str(row['message'])

                # wa uses curly quotes U+201C/U+201D
                name_match = re.search(r'changed the group name to [""\u201C](.+?)[""\u201D]', msg)
                if name_match:
                    new_name = name_match.group(1)
                    group_name_history.append({
                        'name': new_name,
                        'date': row['datetime']
                    })

                create_match = re.search(r'created group [""\u201C](.+?)[""\u201D]', msg)
                if create_match:
                    new_name = create_match.group(1)
                    group_name_history.insert(0, {
                        'name': new_name,
                        'date': row['datetime']
                    })

    # get most recent name
    if group_name_history:
        group_name_history.sort(key=lambda x: x['date'])
        current_group_name = group_name_history[-1]['name']
        print(f"  Group name: '{current_group_name}'")
        if len(group_name_history) > 1:
            print(f"  (renamed {len(group_name_history)} times)")

    # also catch generic system senders
    for sender in df['sender'].unique():
        if sender.lower() in ['you', 'group', 'admin']:
            group_names.add(sender)

    if group_names:
        for name in group_names:
            if name != current_group_name:
                count = len(df[df['sender'] == name])
                print(f"  Filtered sender: '{name}' ({count} msgs)")

    # mark as system
    if group_names:
        df = df.copy()
        df.loc[df['sender'].isin(group_names), 'is_system'] = True

    return df, group_names, current_group_name


def merge_similar_contacts(df):
    # merge renamed contacts like "sanjjit s cse g2 ssn" -> "sanjjit s"
    if df.empty:
        return df

    senders = df['sender'].unique().tolist()
    name_mapping = {}

    for i, name1 in enumerate(senders):
        if name1 in name_mapping:
            continue

        for name2 in senders[i+1:]:
            if name2 in name_mapping:
                continue

            n1_lower = name1.lower().strip()
            n2_lower = name2.lower().strip()

            # prefix match - common for contact renames
            if n1_lower.startswith(n2_lower) or n2_lower.startswith(n1_lower):
                # shorter = canonical
                if len(name1) <= len(name2):
                    canonical, old = name1, name2
                else:
                    canonical, old = name2, name1

                name_mapping[old] = canonical

            # first name match
            elif n1_lower.split()[0] == n2_lower.split()[0] and len(n1_lower.split()[0]) > 3:
                words1 = set(n1_lower.split())
                words2 = set(n2_lower.split())

                # college/institution indicators
                inst_indicators = {'ssn', 'cse', 'ece', 'eee', 'mech', 'bme', 'chem', 'civil',
                                   'g1', 'g2', 'g3', 's1', 's2', 's3', 'a1', 'a2', 'b1', 'b2'}

                has_inst1 = bool(words1 & inst_indicators)
                has_inst2 = bool(words2 & inst_indicators)

                if has_inst1 != has_inst2:
                    # one without inst suffix = canonical
                    if has_inst1:
                        canonical, old = name2, name1
                    else:
                        canonical, old = name1, name2

                    canonical_words = set(canonical.lower().split())
                    old_words = set(old.lower().split())

                    if canonical_words.issubset(old_words):
                        name_mapping[old] = canonical

    if name_mapping:
        df = df.copy()
        df['sender'] = df['sender'].replace(name_mapping)

        for old, new in name_mapping.items():
            print(f"  Merged: '{old}' -> '{new}'")

    return df


def extract_emojis(text):
    return [c for c in text if c in emoji.EMOJI_DATA]
