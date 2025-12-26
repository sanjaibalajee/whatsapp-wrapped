"""
Processing service - wraps existing parser and stats modules
"""

import sys
from pathlib import Path

# Ensure root is in path for core package imports
ROOT_DIR = Path(__file__).parent.parent.parent.parent  # whatsapp-wrapped/

for path in ["/app", str(ROOT_DIR)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import from core package
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

    # Check for WhatsApp message pattern
    pattern = r'\[\d{2}/\d{2}/\d{2},\s\d{1,2}:\d{2}:\d{2}\s[APM]{2}\]'
    matches = re.findall(pattern, content[:5000])  # Check first 5KB

    if len(matches) < 3:
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
    words = get_word_stats(df, user_df, top_n=30)

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

    # Step 12: Compile results
    update_progress(95, "Compiling results...")

    # Convert response_pairs keys from tuple to string
    response_pairs_serializable = {
        f"{k[0]} → {k[1]}": v for k, v in response_pairs.items()
    } if response_pairs else {}

    # Convert date keys to strings
    busiest_dates_serializable = {
        str(k): v for k, v in busiest_dates.items()
    } if busiest_dates else {}

    result = {
        "metadata": {
            "year": year,
            "total_messages_in_file": total_before,
            "messages_in_year": len(df),
            "group_name": current_group_name,
        },
        "basic_stats": basic_stats,
        "top_chatters": top_chatters,
        "hourly_activity": hourly,
        "daily_activity": daily,
        "streak_stats": streak_stats,
        "emoji_stats": {
            "overall": emojis,
            "by_user": user_emojis,
        },
        "media_stats": media,
        "word_stats": words,
        "conversation_starters": starters,
        "night_owls": night_owls,
        "early_birds": early_birds,
        "longest_messages": longest_msgs,
        "busiest_dates": busiest_dates_serializable,
        "response_pairs": response_pairs_serializable,
        "double_texters": double_texters,
        "conversation_killers": conv_killers,
        "response_times": response_times,
        "caps_users": caps_users,
        "question_askers": question_askers,
        "link_sharers": link_sharers,
        "one_worders": one_worders,
        "monologuers": monologuers,
        "laugh_stats": laugh_stats,
        "unique_words": unique_words,
        "catchphrases": catchphrases,
        "personality_tags": personality_tags,
        "group_vibe": group_vibe,
        "topics": topics,
    }

    update_progress(100, "Complete")

    return result
