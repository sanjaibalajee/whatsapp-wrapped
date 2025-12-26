# display - rich cli output

import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from core.roasts import generate_roast

console = Console()


def display_header(basic_stats, group_name=None, year=2025):
    console.print()

    if group_name:
        header_text = (
            f"[bold magenta]WhatsApp Wrapped {year}[/bold magenta]\n"
            f"[cyan]{group_name}[/cyan]\n"
            f"[dim]Your year in messages[/dim]"
        )
    else:
        header_text = (
            f"[bold magenta]WhatsApp Wrapped {year}[/bold magenta]\n"
            f"[dim]Your year in messages[/dim]"
        )

    console.print(Panel.fit(
        header_text,
        border_style="magenta",
        padding=(1, 4)
    ))
    console.print()


def display_basic_stats(stats):
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
    if not chatters:
        return

    table = Table(title="Top Chatters", box=box.ROUNDED, border_style="green")
    table.add_column("Rank", style="dim", width=4)
    table.add_column("Member", style="cyan")
    table.add_column("Messages", justify="right", style="green")
    table.add_column("", width=20)

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
    if not hourly:
        return

    console.print(Panel("[bold]When You're Most Active[/bold]", border_style="yellow"))

    max_count = max(hourly.values()) if hourly else 1

    for hour in range(24):
        count = hourly.get(hour, 0)
        bar_length = int((count / max_count) * 30) if max_count > 0 else 0
        bar = "" * bar_length

        if 0 <= hour < 6:
            color = "blue"
        elif 6 <= hour < 12:
            color = "yellow"
        elif 12 <= hour < 18:
            color = "green"
        else:
            color = "magenta"

        time_label = f"{hour:02d}:00"
        console.print(f"   {time_label} [{color}]{bar}[/{color}] {count}")

    console.print()


def display_daily_activity(daily):
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
    if not emojis:
        console.print("[dim]No emojis found[/dim]")
        return

    emoji_str = "  ".join([f"{e} ({c})" for e, c in list(emojis.items())[:10]])
    console.print(Panel(
        f"[bold]Most Used Emojis[/bold]\n\n{emoji_str}",
        border_style="yellow"
    ))

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
    if media.get('total', 0) == 0:
        return

    table = Table(title="Media Shared", box=box.ROUNDED, border_style="magenta")
    table.add_column("Type", style="cyan")
    table.add_column("Count", justify="right", style="green")

    icons = {
        "image": "", "video": "", "sticker": "", "audio": "",
        "gif": "", "document": "", "contact": "", "location": ""
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


def display_word_stats(words, full=False):
    if not words:
        return

    word_list = []
    max_count = max(words.values())

    # show all words with counts in full mode
    if full:
        for word, count in words.items():
            word_list.append(f"{word} ({count})")
        console.print(Panel(
            "  ".join(word_list),
            title="Most Used Words (Full)",
            border_style="blue"
        ))
    else:
        for word, count in words.items():
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
    if starters:
        starter_list = list(starters.items())[:3]
        starter_text = "\n".join([f"  {i+1}. {name} ({count} times)"
                                   for i, (name, count) in enumerate(starter_list)])
        console.print(Panel(
            f"[bold]Conversation Starters[/bold]\n{starter_text}",
            border_style="green"
        ))

    if night_owls or early_birds:
        cols = []
        if night_owls:
            owl_text = "\n".join([f"  {name}: {count}" for name, count in list(night_owls.items())[:3]])
            cols.append(f"[bold] Night Owls[/bold]\n[dim](12am-5am)[/dim]\n{owl_text}")
        if early_birds:
            bird_text = "\n".join([f"  {name}: {count}" for name, count in list(early_birds.items())[:3]])
            cols.append(f"[bold] Early Birds[/bold]\n[dim](5am-8am)[/dim]\n{bird_text}")
        console.print(Panel("\n\n".join(cols), border_style="blue"))

    if longest_msgs:
        long_text = "\n".join([f"  {name}: ~{int(length)} chars avg"
                               for name, length in list(longest_msgs.items())[:3]])
        console.print(Panel(
            f"[bold] Essay Writers[/bold]\n[dim](Longest avg messages)[/dim]\n{long_text}",
            border_style="cyan"
        ))

    console.print()


def display_busiest_dates(dates):
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
    if not pairs:
        return

    table = Table(title="Chat Dynamics (Who Replies to Whom)", box=box.ROUNDED, border_style="cyan")
    table.add_column("Sender", style="cyan")
    table.add_column("", width=3)
    table.add_column("Replier", style="green")
    table.add_column("Times", justify="right")

    for (sender, replier), count in list(pairs.items())[:7]:
        s_name = sender[:15] + "..." if len(sender) > 15 else sender
        r_name = replier[:15] + "..." if len(replier) > 15 else replier
        table.add_row(s_name, "", r_name, str(count))

    console.print(table)
    console.print()


def display_response_times(response_times):
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
    if not personality_tags:
        return

    console.print(Panel("[bold]Personality Profiles[/bold]", border_style="magenta"))

    for sender, tags in list(personality_tags.items())[:8]:
        name = sender.split()[0]
        tag_strs = [f"{t['icon']} {t['tag'].replace('_', ' ')}" for t in tags[:4]]
        console.print(f"  [cyan]{name}[/cyan]: {' | '.join(tag_strs)}")

    console.print()


def display_unique_words(unique_words, full=False):
    if not unique_words:
        return

    title = "Signature Words (TF-IDF)" + (" - Full" if full else "")
    table = Table(title=title, box=box.ROUNDED, border_style="blue")
    table.add_column("Member", style="cyan")
    table.add_column("Their Words", style="dim")

    # show all users and more words in full mode
    user_limit = None if full else 6
    word_limit = 10 if full else 5

    for sender, words in list(unique_words.items())[:user_limit]:
        name = sender[:15] + "..." if len(sender) > 15 else sender
        word_list = list(words.keys())[:word_limit]
        table.add_row(name, ", ".join(word_list))

    console.print(table)
    console.print()


def display_catchphrases(catchphrases, full=False):
    if not catchphrases:
        return

    console.print(Panel("[bold]Catchphrases[/bold]", border_style="yellow"))

    # show all users and phrases in full mode
    user_limit = None if full else 5
    phrase_limit = 5 if full else 1

    for sender, phrases in list(catchphrases.items())[:user_limit]:
        name = sender.split()[0]
        for phrase_info in phrases[:phrase_limit]:
            console.print(f"  [cyan]{name}[/cyan]: \"{phrase_info['phrase']}\" ({phrase_info['count']}x)")

    console.print()


def display_group_vibe(vibe, full=False):
    if not vibe or not vibe.get('description'):
        return

    personality = ", ".join(vibe.get('personality', [])[:4])
    # show all topics in full mode
    topic_limit = None if full else 6
    topics = ", ".join(vibe.get('topics', [])[:topic_limit])

    content = f"[bold]Energy:[/bold] {vibe.get('energy', 'unknown').upper()}\n"
    content += f"[bold]Personality:[/bold] {personality}\n"
    content += f"[bold]Peak Time:[/bold] {vibe.get('peak_time', 'unknown')}\n"
    content += f"[bold]Hot Topics:[/bold] {topics}\n\n"
    content += f"[dim italic]{vibe.get('description', '')}[/dim italic]"

    console.print(Panel(content, title="Group Vibe", border_style="magenta"))
    console.print()


def display_roasts(personality_tags, unique_words, catchphrases):
    if not personality_tags:
        return

    console.print(Panel("[bold red]The Roast Section[/bold red]", border_style="red"))

    for sender, tags in personality_tags.items():
        roast = generate_roast(sender, tags, unique_words, catchphrases)
        if roast:
            console.print(f"  [yellow]{roast}[/yellow]")

    console.print()


def display_streak_stats(streak_stats):
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
    # debug view for llm context
    console.print(Panel("[bold]LLM Context Preview[/bold]", border_style="dim"))
    console.print(f"[dim]Context size: ~{len(json.dumps(context))} chars[/dim]")
    console.print(f"[dim]Participants: {len(context.get('person_profiles', {}))}[/dim]")
    console.print(f"[dim]Sample messages: {len(context.get('sample_messages', []))}[/dim]")
    console.print()
