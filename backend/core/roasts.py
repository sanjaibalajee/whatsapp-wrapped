# roasts - personality tags and roast generation

import random

from .stats import (
    get_double_texters, get_conversation_killers, get_response_times,
    get_caps_users, get_question_askers, get_link_sharers, get_one_worders,
    get_night_owls, get_early_birds, get_monologuers, get_laugh_stats,
    get_top_chatters, get_longest_messages, get_conversation_starters,
    get_media_stats, get_emoji_stats_by_user
)


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


def assign_personality_tags(df, stats_cache=None):
    user_df = df[~df['is_system']]
    senders = user_df['sender'].unique()

    # compute if not cached
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

        if msg_count < 5:
            continue

        msg_share = msg_count / total_msgs * 100

        # activity
        if sender in stats_cache['top_chatters']:
            rank = list(stats_cache['top_chatters'].keys()).index(sender) + 1
            if rank == 1:
                tags.append({"tag": "chatterbox", "detail": f"#{rank} with {msg_count} messages", "icon": ""})
            elif rank <= 3:
                tags.append({"tag": "active_member", "detail": f"#{rank} most active", "icon": ""})

        if msg_share < 5 and msg_count > 10:
            tags.append({"tag": "lurker", "detail": f"Only {msg_share:.1f}% of messages", "icon": ""})

        # timing - can only be one: night owl OR early bird, not both
        night_count = stats_cache['night_owls'].get(sender, 0)
        morning_count = stats_cache['early_birds'].get(sender, 0)

        if night_count > 20 or morning_count > 10:
            # pick the dominant one
            if night_count > morning_count * 1.5:
                tags.append({"tag": "night_owl", "detail": f"{night_count} late night msgs", "icon": ""})
            elif morning_count > night_count * 1.5:
                tags.append({"tag": "early_bird", "detail": f"{morning_count} early msgs", "icon": ""})
            elif night_count > morning_count:
                tags.append({"tag": "night_owl", "detail": f"{night_count} late night msgs", "icon": ""})
            elif morning_count > 0:
                tags.append({"tag": "early_bird", "detail": f"{morning_count} early msgs", "icon": ""})

        # conversation
        if sender in stats_cache['conv_starters']:
            starts = stats_cache['conv_starters'][sender]
            if starts > 10:
                tags.append({"tag": "conversation_starter", "detail": f"Started {starts} convos", "icon": ""})

        if sender in stats_cache['conv_killers']:
            kills = stats_cache['conv_killers'][sender]['kills']
            rate = stats_cache['conv_killers'][sender]['rate']
            if kills > 5 and rate > 10:
                tags.append({"tag": "conversation_killer", "detail": f"{rate}% kill rate", "icon": ""})

        # response
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

        # style
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

        # content
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

        # media
        if 'top_sharers' in stats_cache['media_stats']:
            if sender in stats_cache['media_stats']['top_sharers']:
                media_count = stats_cache['media_stats']['top_sharers'][sender]
                if media_count > 20:
                    tags.append({"tag": "media_king", "detail": f"{media_count} media shared", "icon": ""})

        # emoji
        if sender in stats_cache['emoji_stats']:
            emoji_count = stats_cache['emoji_stats'][sender]['total']
            if emoji_count > 50:
                tags.append({"tag": "emoji_spammer", "detail": f"{emoji_count} emojis used", "icon": ""})

        if tags:
            personality_tags[sender] = tags

    return personality_tags


def generate_roast(person, tags, unique_words, catchphrases):
    if not tags:
        return None

    roast_parts = []

    # pick 2-3 tags
    selected_tags = tags[:min(3, len(tags))]

    for tag_info in selected_tags:
        tag = tag_info['tag']
        if tag in ROAST_TEMPLATES:
            template = random.choice(ROAST_TEMPLATES[tag])
            roast_parts.append(template)

    # add signature word
    if person in unique_words and unique_words[person]:
        top_word = list(unique_words[person].keys())[0]
        roast_parts.append(f"won't stop saying '{top_word}'")

    # add catchphrase
    if person in catchphrases and catchphrases[person]:
        phrase = catchphrases[person][0]['phrase']
        roast_parts.append(f"(trademark phrase: '{phrase}')")

    if not roast_parts:
        return None

    # assemble
    name = person.split()[0]
    roast = f"{name} {roast_parts[0]}"
    if len(roast_parts) > 1:
        roast += f", {roast_parts[1]}"
    if len(roast_parts) > 2:
        roast += f". {roast_parts[2].capitalize()}"

    return roast
