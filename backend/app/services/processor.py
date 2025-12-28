"""
Processing service - wraps existing parser and stats modules
"""

import random
from core.parser import parse_whatsapp_content, detect_group_names, merge_similar_contacts
from core.stats import (
    get_basic_stats, get_top_chatters, get_hourly_activity, get_daily_activity,
    get_emoji_stats, get_emoji_stats_by_user, get_media_stats, get_word_stats,
    get_conversation_starters, get_night_owls, get_early_birds, get_longest_messages,
    get_busiest_dates, get_response_pairs, get_double_texters, get_conversation_killers,
    get_response_times, get_streak_stats, get_caps_users, get_question_askers,
    get_link_sharers, get_one_worders, get_monologuers, get_laugh_stats,
    get_unique_words_per_person, get_catchphrases, get_interesting_topics, get_group_vibe
)
from core.roasts import assign_personality_tags
from .ai import generate_roasts


def quick_parse_participants(content: str) -> tuple[list[str], str | None]:
    """
    Quick parse to extract participants and group name.
    Fast operation suitable for sync execution.

    Returns:
        Tuple of (participants_list, group_name)
    """
    df = parse_whatsapp_content(content)

    if df.empty:
        return [], None

    # Merge similar contacts
    df = merge_similar_contacts(df)

    # Detect group names (filters system senders)
    df, group_names, current_group_name = detect_group_names(df)

    # Get unique non-system senders
    user_df = df[~df['is_system']]
    participants = sorted(user_df['sender'].unique().tolist())

    return participants, current_group_name


def validate_whatsapp_format(content: str) -> tuple[bool, str]:
    """
    Validate if content looks like WhatsApp export

    Returns:
        Tuple of (is_valid, error_message)
    """
    import re

    if not content or len(content.strip()) == 0:
        return False, "File is empty"

    # Check for WhatsApp message pattern (support multiple formats)
    patterns = [
        r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?::\d{2})?\s?(?:[APap][Mm])?\]',  # Bracketed
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?::\d{2})?\s?(?:[APap][Mm])?\s?[-–]',  # Non-bracketed
    ]

    total_matches = 0
    for pattern in patterns:
        matches = re.findall(pattern, content[:5000])
        total_matches += len(matches)

    if total_matches < 3:
        return False, "File doesn't appear to be a WhatsApp export"

    return True, ""


def process_chat(file_content: str, year: int = 2025, selected_members: list[str] = None, progress_callback=None) -> dict:
    """
    Process WhatsApp chat and return all stats

    Args:
        file_content: Raw text content of WhatsApp export
        year: Year to filter messages
        selected_members: List of members to include in analysis (None = all)
        progress_callback: Optional callback(progress: int, step: str)

    Returns:
        Dictionary with all computed statistics
    """
    import time
    import logging
    logger = logging.getLogger(__name__)

    start_time = time.time()
    last_time = start_time

    def update_progress(progress: int, step: str):
        nonlocal last_time
        now = time.time()
        elapsed = (now - last_time) * 1000  # ms
        total = (now - start_time) * 1000
        logger.info(f"[{total:7.0f}ms] (+{elapsed:5.0f}ms) {progress:3d}% | {step}")
        last_time = now
        if progress_callback:
            progress_callback(progress, step)

    # Step 1: Parse
    update_progress(10, "Parsing messages...")
    df = parse_whatsapp_content(file_content)

    if df.empty:
        raise ValueError("No messages found in file")

    # Step 2: Merge contacts
    update_progress(15, "Merging contacts...")
    df = merge_similar_contacts(df)

    # Step 3: Detect group names
    update_progress(20, "Detecting group info...")
    df, group_names, current_group_name = detect_group_names(df)

    # Step 4: Filter by year
    update_progress(25, f"Filtering to {year}...")
    total_before = len(df)
    df = df[df['datetime'].dt.year == year].copy()

    if df.empty:
        raise ValueError(f"No messages found for {year}")

    # Step 4.5: Filter by selected members (if specified)
    if selected_members:
        update_progress(27, "Filtering to selected members...")
        df = df[df['sender'].isin(selected_members) | df['is_system']].copy()

    # Pre-filter user messages
    user_df = df[~df['is_system']].copy()

    if user_df.empty:
        raise ValueError("No user messages found after filtering")

    # Step 5: Basic stats
    update_progress(30, "Calculating basic stats...")
    basic_stats = get_basic_stats(df, user_df)
    top_chatters = get_top_chatters(df, user_df)

    # Step 6: Activity patterns
    update_progress(40, "Analyzing activity patterns...")
    hourly = get_hourly_activity(df, user_df)
    daily = get_daily_activity(df, user_df)
    streak_stats = get_streak_stats(df, user_df)

    # Step 7: Emoji and media
    update_progress(50, "Analyzing emojis and media...")
    emojis = get_emoji_stats(df, user_df)
    user_emojis = get_emoji_stats_by_user(df, user_df)
    media = get_media_stats(df, user_df)
    words = get_word_stats(df, user_df, top_n=100)

    # Step 8: Conversation patterns
    update_progress(60, "Analyzing conversation patterns...")
    starters = get_conversation_starters(df, user_df)
    night_owls = get_night_owls(df, user_df)
    early_birds = get_early_birds(df, user_df)
    longest_msgs = get_longest_messages(df, user_df)
    busiest_dates = get_busiest_dates(df, user_df)
    response_pairs = get_response_pairs(df, user_df)

    # Step 9: Behavioral stats
    update_progress(70, "Analyzing behavioral patterns...")
    double_texters = get_double_texters(df, user_df)
    conv_killers = get_conversation_killers(df, user_df)
    response_times = get_response_times(df, user_df)
    caps_users = get_caps_users(df, user_df)
    question_askers = get_question_askers(df, user_df)
    link_sharers = get_link_sharers(df, user_df)
    one_worders = get_one_worders(df, user_df)
    monologuers = get_monologuers(df, user_df)
    laugh_stats = get_laugh_stats(df, user_df)

    # Step 10: Unique words and catchphrases
    update_progress(80, "Extracting signature words...")
    unique_words = get_unique_words_per_person(df, user_df, top_n=10)
    catchphrases = get_catchphrases(df, user_df)

    # Step 11: Personality profiles
    update_progress(90, "Building personality profiles...")
    stats_cache = {
        'double_texters': double_texters,
        'conv_killers': conv_killers,
        'response_times': response_times,
        'caps_users': caps_users,
        'question_askers': question_askers,
        'link_sharers': link_sharers,
        'one_worders': one_worders,
        'night_owls': night_owls,
        'early_birds': early_birds,
        'monologuers': monologuers,
        'laugh_stats': laugh_stats,
        'top_chatters': top_chatters,
        'longest_msgs': longest_msgs,
        'conv_starters': starters,
        'media_stats': media,
        'emoji_stats': user_emojis,
    }

    personality_tags = assign_personality_tags(df, stats_cache)
    group_vibe = get_group_vibe(df, emojis, hourly, user_df)
    topics = get_interesting_topics(df, user_df)

    # Step 12: Generate AI roasts
    update_progress(92, "Judging your year...")
    peak_hour_for_ai = max(hourly.items(), key=lambda x: x[1])[0] if hourly else None
    top_words_for_ai = list(words.items())[:30] if words else []

    # Limit to top 10 active members for AI roasts
    top_10_chatters = dict(list(top_chatters.items())[:10])

    # Extract sample messages for each person (interesting/longer messages)
    sample_messages = {}
    text_only_df = user_df[user_df['media_type'].isna()].copy()
    for person in top_10_chatters.keys():
        person_msgs = text_only_df[text_only_df['sender'] == person]['message'].tolist()
        # Filter for interesting messages (longer than 5 words, not too long)
        interesting = [
            msg for msg in person_msgs
            if isinstance(msg, str) and 5 < len(msg.split()) < 30 and not msg.startswith('http')
        ]
        # Get a random sample of messages
        if len(interesting) > 10:
            sample_messages[person] = random.sample(interesting, 10)
        else:
            sample_messages[person] = interesting[:10]

    ai_roasts = generate_roasts(
        group_name=current_group_name,
        year=year,
        total_messages=len(user_df),
        total_participants=user_df['sender'].nunique(),
        peak_hour=peak_hour_for_ai,
        topics=topics,
        top_words=top_words_for_ai,
        top_chatters=top_10_chatters,
        signature_words=unique_words,
        personality_tags=personality_tags,
        user_emojis=user_emojis,
        night_owls=night_owls,
        early_birds=early_birds,
        double_texters=double_texters,
        response_times=response_times,
        caps_users=caps_users,
        question_askers=question_askers,
        one_worders=one_worders,
        sample_messages=sample_messages,
    )

    # Step 13: Compile results into slides
    update_progress(95, "Compiling results...")

    # Helper: get top N from dict
    def top_n(d, n):
        if not d:
            return {}
        return dict(list(d.items())[:n])

    # Convert date keys to strings
    busiest_dates_serializable = {
        str(k): v for k, v in busiest_dates.items()
    } if busiest_dates else {}

    # Build group totals for slide 1
    media_by_type = media.get("by_type", {}) if media else {}
    total_messages = int(basic_stats.get("total_messages", 0)) if basic_stats else 0
    total_participants = int(basic_stats.get("total_participants", 0)) if basic_stats else 0

    group_totals = {
        "total_messages": total_messages,
        "total_images": int(media_by_type.get("image", 0)),
        "total_videos": int(media_by_type.get("video", 0)),
        "total_gifs": int(media_by_type.get("gif", 0)),
        "total_stickers": int(media_by_type.get("sticker", 0)),
        "total_audio": int(media_by_type.get("audio", 0)),
        "total_documents": int(media_by_type.get("document", 0)),
    }

    # Find peak hour (single most active hour)
    peak_hour = int(max(hourly.items(), key=lambda x: x[1])[0]) if hourly else None

    # Find busiest day
    busiest_day = list(busiest_dates_serializable.items())[0] if busiest_dates_serializable else None

    # For 2-person chats, show only 1 person for starters/killers
    top_n_for_dynamics = 1 if total_participants == 2 else 2
    starters_top = list(starters.keys())[:top_n_for_dynamics] if starters else []
    killers_top = list(conv_killers.keys())[:top_n_for_dynamics] if conv_killers else []

    # For 2-person chats, set group name to "chat between X and Y"
    participants_list = list(top_chatters.keys())
    if total_participants == 2 and len(participants_list) >= 2:
        display_group_name = f"chat between {participants_list[0]} and {participants_list[1]}"
    else:
        display_group_name = current_group_name

    # Build chat dynamics for graph (max 7 people)
    chat_dynamics = []
    top_7_people = list(top_chatters.keys())[:7]
    for person in top_7_people:
        person_df = user_df[user_df['sender'] == person]
        # messages per day of week
        daily_dist = {k: int(v) for k, v in person_df['day_of_week'].value_counts().to_dict().items()}
        chat_dynamics.append({
            "name": person,
            "messages": int(top_chatters.get(person, 0)),
            "daily_distribution": daily_dist,
        })

    # Signature words per person (top 4 each)
    signature_words = {}
    for person, words_dict in unique_words.items():
        # words_dict is a dict like {"word": {"score": ..., "count": ...}}
        signature_words[person] = list(words_dict.keys())[:4] if words_dict else []

    # Build slides
    slides = [
        {
            "id": 1,
            "title": "your year in messages",
            "type": "overview",
            "data": {
                "year": year,
                "total_participants": total_participants,
                "streak": streak_stats,
                **group_totals,
            }
        },
        {
            "id": 2,
            "title": "top chatters",
            "type": "ranking",
            "data": {
                "rankings": [{"name": k, "count": int(v)} for k, v in top_chatters.items()]
            }
        },
        {
            "id": 3,
            "title": "emoji game",
            "type": "emojis",
            "data": {
                "group_top_emojis": [[e, int(c)] for e, c in list(emojis.items())[:10]] if emojis else [],
                "per_person": {k: [[e, int(c)] for e, c in v.get("top", {}).items()] for k, v in user_emojis.items()} if user_emojis else {}
            }
        },
        {
            "id": 4,
            "title": "peak activity",
            "type": "activity",
            "data": {
                "busiest_day": {"date": busiest_day[0], "count": int(busiest_day[1])} if busiest_day else None,
                "peak_hour": peak_hour,
                "peak_hour_formatted": f"{peak_hour}:00" if peak_hour is not None else None,
                "hourly_distribution": {int(k): int(v) for k, v in hourly.items()} if hourly else {},
                "daily_distribution": {k: int(v) for k, v in daily.items()} if daily else {},
            }
        },
        {
            "id": 5,
            "title": "word cloud",
            "type": "words",
            "data": {
                "top_words": [[w, int(c)] for w, c in list(words.items())[:100]] if words else [],
                "topics": topics[:4] if topics else [],
            }
        },
        {
            "id": 6,
            "title": "signature words",
            "type": "signature_words",
            "data": {
                "per_person": signature_words
            }
        },
        {
            "id": 7,
            "title": "conversation dynamics",
            "type": "convo_dynamics",
            "data": {
                "starters": starters_top,
                "killers": killers_top,
            }
        },
        {
            "id": 8,
            "title": "chat patterns",
            "type": "chat_graph",
            "data": {
                "members": chat_dynamics,
            }
        },
        {
            "id": 9,
            "title": "fun stats",
            "type": "fun_stats",
            "data": {
                "double_texter": [list(double_texters.keys())[0], int(list(double_texters.values())[0])] if double_texters else None,
                "caps_lock_user": [list(caps_users.keys())[0], int(list(caps_users.values())[0].get("caps_messages", 0))] if caps_users else None,
                "question_asker": [list(question_askers.keys())[0], int(list(question_askers.values())[0].get("questions", 0))] if question_askers else None,
                "link_sharer": [list(link_sharers.keys())[0], int(list(link_sharers.values())[0])] if link_sharers else None,
            }
        },
        {
            "id": 10,
            "title": "ai roasts",
            "type": "ai_roasts",
            "data": {
                "brainrot_score": ai_roasts.get("brainrot_score", 50),
                "group_roast": ai_roasts.get("group_roast", []),
                "individual_roasts": ai_roasts.get("individual_roasts", {}),
            }
        },
    ]

    result = {
        "metadata": {
            "year": year,
            "total_messages_in_file": total_before,
            "messages_in_year": len(df),
            "group_name": display_group_name,
            "participants": list(top_chatters.keys()),
        },
        "basic_stats": {
            "total_messages": total_messages,
            "total_participants": total_participants,
        },
        "slides": slides,
    }

    update_progress(100, "Complete")

    return result
