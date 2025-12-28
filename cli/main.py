# whatsapp wrapped - entry point

import sys
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add backend to path for core module
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from core.parser import parse_whatsapp, detect_group_names, merge_similar_contacts
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
from .display import (
    display_header, display_basic_stats, display_group_vibe, display_top_chatters,
    display_streak_stats, display_hourly_activity, display_daily_activity,
    display_response_times, display_emoji_stats, display_media_stats, display_word_stats,
    display_unique_words, display_catchphrases, display_special_stats,
    display_double_texters, display_conversation_killers, display_busiest_dates,
    display_response_pairs, display_personality_tags, display_roasts, display_llm_context
)

console = Console()


def prepare_llm_context(df, user_df=None, max_sample_messages=50):
    # condense everything for llm consumption
    if user_df is None:
        user_df = df[~df['is_system']]

    basic_stats = get_basic_stats(df, user_df)
    emoji_stats = get_emoji_stats(df, user_df)
    hourly = get_hourly_activity(df, user_df)

    stats_cache = {
        'double_texters': get_double_texters(df, user_df),
        'conv_killers': get_conversation_killers(df, user_df),
        'response_times': get_response_times(df, user_df),
        'caps_users': get_caps_users(df, user_df),
        'question_askers': get_question_askers(df, user_df),
        'link_sharers': get_link_sharers(df, user_df),
        'one_worders': get_one_worders(df, user_df),
        'night_owls': get_night_owls(df, user_df),
        'early_birds': get_early_birds(df, user_df),
        'monologuers': get_monologuers(df, user_df),
        'laugh_stats': get_laugh_stats(df, user_df),
        'top_chatters': get_top_chatters(df, user_df),
        'longest_msgs': get_longest_messages(df, user_df),
        'conv_starters': get_conversation_starters(df, user_df),
        'media_stats': get_media_stats(df, user_df),
        'emoji_stats': get_emoji_stats_by_user(df, user_df),
    }

    personality_tags = assign_personality_tags(df, stats_cache)
    unique_words = get_unique_words_per_person(df, user_df)
    catchphrases = get_catchphrases(df, user_df)
    group_vibe = get_group_vibe(df, emoji_stats, hourly, user_df)

    # sample msgs proportionally
    sample_messages = []
    text_df = user_df[(user_df['media_type'].isna()) & (user_df['char_count'] > 10)]

    if not text_df.empty:
        for sender in text_df['sender'].unique():
            sender_msgs = text_df[text_df['sender'] == sender]
            n_sample = min(max_sample_messages // len(text_df['sender'].unique()), len(sender_msgs))
            if n_sample > 0:
                sampled = sender_msgs.sample(n=min(n_sample, len(sender_msgs)))
                for _, row in sampled.iterrows():
                    sample_messages.append({
                        "sender": row['sender'],
                        "message": row['message'][:200],
                        "hour": row['hour']
                    })

    # build profiles
    person_profiles = {}
    for sender in user_df['sender'].unique():
        sender_df = user_df[user_df['sender'] == sender]
        if len(sender_df) < 5:
            continue

        profile = {
            "message_count": len(sender_df),
            "message_share": round(len(sender_df) / len(user_df) * 100, 1),
        }

        if sender in personality_tags:
            profile["tags"] = [t["tag"] for t in personality_tags[sender]]

        if sender in unique_words:
            profile["signature_words"] = list(unique_words[sender].keys())[:5]

        if sender in catchphrases:
            profile["catchphrases"] = [p["phrase"] for p in catchphrases[sender][:3]]

        if sender in stats_cache['emoji_stats']:
            profile["top_emojis"] = list(stats_cache['emoji_stats'][sender]['top'].keys())

        person_profiles[sender] = profile

    context = {
        "group_overview": {
            "total_messages": basic_stats["total_messages"] if basic_stats else 0,
            "participants": list(person_profiles.keys()),
            "date_range": f"{basic_stats['first_message'].strftime('%Y-%m-%d')} to {basic_stats['last_message'].strftime('%Y-%m-%d')}" if basic_stats else "",
            "vibe": group_vibe,
        },
        "top_topics": get_interesting_topics(df, user_df)[:15],
        "top_emojis": list(emoji_stats.keys())[:10] if emoji_stats else [],
        "person_profiles": person_profiles,
        "sample_messages": sample_messages[:max_sample_messages],
    }

    return context, personality_tags, unique_words, catchphrases, group_vibe


def run_wrapped(file_path, show_llm_context=False, year=2025, full=False):
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

    # merge renamed contacts first
    df = merge_similar_contacts(df)

    # then detect group names
    df, group_names, current_group_name = detect_group_names(df)

    # filter to target year only - this is WRAPPED not all-time stats
    total_before = len(df)
    df = df[df['datetime'].dt.year == year].copy()
    total_after = len(df)

    if df.empty:
        console.print(f"[red]No messages found for {year}![/red]")
        console.print(f"[dim]Total messages in file: {total_before}[/dim]")
        return

    console.print(f"[dim]Filtered to {year}: {total_after:,} messages (from {total_before:,} total)[/dim]")

    # verify filter worked
    years_in_data = df['datetime'].dt.year.unique()
    if len(years_in_data) > 1 or (len(years_in_data) == 1 and years_in_data[0] != year):
        console.print(f"[red]WARNING: Filter issue! Years in data: {sorted(years_in_data)}[/red]")

    # pre-filter user messages once - pass to all stats functions
    user_df = df[~df['is_system']].copy()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Analyzing chat patterns...", total=None)

        # basic stats - pass user_df to avoid repeated filtering
        basic_stats = get_basic_stats(df, user_df)
        top_chatters = get_top_chatters(df, user_df)
        hourly = get_hourly_activity(df, user_df)
        daily = get_daily_activity(df, user_df)

        progress.update(task, description="Analyzing emojis and media...")
        emojis = get_emoji_stats(df, user_df)
        user_emojis = get_emoji_stats_by_user(df, user_df)
        media = get_media_stats(df, user_df)
        words = get_word_stats(df, user_df, top_n=50 if full else 20)

        progress.update(task, description="Analyzing conversation patterns...")
        starters = get_conversation_starters(df, user_df)
        night_owls = get_night_owls(df, user_df)
        early_birds = get_early_birds(df, user_df)
        longest_msgs = get_longest_messages(df, user_df)
        busiest_dates = get_busiest_dates(df, user_df)
        response_pairs = get_response_pairs(df, user_df)

        progress.update(task, description="Analyzing behavioral patterns...")
        double_texters = get_double_texters(df, user_df)
        conv_killers = get_conversation_killers(df, user_df)
        response_times = get_response_times(df, user_df)
        streak_stats = get_streak_stats(df, user_df)

        progress.update(task, description="Extracting signature words...")
        unique_words = get_unique_words_per_person(df, user_df, top_n=15 if full else 10)
        catchphrases = get_catchphrases(df, user_df)

        progress.update(task, description="Building personality profiles...")
        stats_cache = {
            'double_texters': double_texters,
            'conv_killers': conv_killers,
            'response_times': response_times,
            'caps_users': get_caps_users(df, user_df),
            'question_askers': get_question_askers(df, user_df),
            'link_sharers': get_link_sharers(df, user_df),
            'one_worders': get_one_worders(df, user_df),
            'night_owls': night_owls,
            'early_birds': early_birds,
            'monologuers': get_monologuers(df, user_df),
            'laugh_stats': get_laugh_stats(df, user_df),
            'top_chatters': top_chatters,
            'longest_msgs': longest_msgs,
            'conv_starters': starters,
            'media_stats': media,
            'emoji_stats': user_emojis,
        }

        personality_tags = assign_personality_tags(df, stats_cache)
        group_vibe = get_group_vibe(df, emojis, hourly, user_df, full=full)

    console.print()

    # display everything
    display_header(basic_stats, current_group_name, year)
    display_basic_stats(basic_stats)
    display_group_vibe(group_vibe, full=full)
    display_top_chatters(top_chatters)
    display_streak_stats(streak_stats)
    display_hourly_activity(hourly)
    display_daily_activity(daily)
    display_response_times(response_times)
    display_emoji_stats(emojis, user_emojis)
    display_media_stats(media)
    display_word_stats(words, full=full)
    display_unique_words(unique_words, full=full)
    display_catchphrases(catchphrases, full=full)
    display_special_stats(starters, night_owls, early_birds, longest_msgs)
    display_double_texters(double_texters)
    display_conversation_killers(conv_killers)
    display_busiest_dates(busiest_dates)
    display_response_pairs(response_pairs)
    display_personality_tags(personality_tags)
    display_roasts(personality_tags, unique_words, catchphrases)

    # llm context for future ai stuff
    if show_llm_context:
        llm_context, _, _, _, _ = prepare_llm_context(df, user_df)
        display_llm_context(llm_context)

        with open("llm_context.json", "w") as f:
            json.dump(llm_context, f, indent=2, default=str)
        console.print("[dim]LLM context saved to llm_context.json[/dim]\n")

    console.print(Panel.fit(
        "[bold green]That's a wrap![/bold green]\n"
        "[dim]Thanks for the memories[/dim]",
        border_style="green",
        padding=(1, 4)
    ))


if __name__ == "__main__":
    file_path = "chat.txt"
    show_llm = False
    full_output = False
    target_year = 2025  # default to current wrapped year

    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--llm-context":
            show_llm = True
        elif arg == "--full":
            full_output = True
        elif arg == "--year" and i + 2 < len(sys.argv):
            target_year = int(sys.argv[i + 2])
        elif arg.isdigit() and sys.argv[i] == "--year":
            pass  # already handled
        elif not arg.startswith("-"):
            file_path = arg

    run_wrapped(file_path, show_llm_context=show_llm, year=target_year, full=full_output)
