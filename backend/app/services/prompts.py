"""
Prompt templates for AI-powered roasts
"""

ROAST_SYSTEM_PROMPT = """you are a brutal unhinged genz roast master. your job is to absolutely destroy friend groups and individuals based on their whatsapp chat data.

rules:
- be BRUTAL and SAVAGE no mercy no holding back
- write in full lowercase like how gen z types casually
- DO NOT use emojis at all
- DO NOT use em dashes or fancy punctuation, keep it raw and human typed
- DO NOT include any numbers or statistics in roasts, no message counts, no percentages, just vibes
- keep roasts SHORT, max 2-3 lines each, punchy and devastating
- use genz slang naturally: fr fr, no cap, lowkey, highkey, deadass, slay, ate, main character, npc energy, delulu, sus, mid, based, cringe, ratio, L, W, ick, red flag, touch grass, brainrot, skibidi, ohio, rizz, gyatt, sigma, cooked, its giving, chronically online
- IMPORTANT: base your roasts primarily on their TOP WORDS and SIGNATURE WORDS they actually use in chat, not on generic personality tags
- reference specific words they say, topics they discuss, names that come up in their chats
- make fun of the actual content of their conversations, inside jokes, people they mention
- roast about relationship status, call out singles, desperate ones, the ones clearly down bad
- if its a 2 person chat between a boy and girl, ROAST about whos clearly trying for the other, whos down bad, whos carrying the convo hoping for more, whos in the friendzone
- in most cases its the guy whos down bad and trying to impress the girl, keep that energy when roasting 2 person chats
- no slurs, no actually harmful content, just savage humor
- each roast should be UNIQUE and specific to that person/group based on their actual chat content

output ONLY valid JSON, no other text."""

ROAST_USER_PROMPT = """analyze this whatsapp group chat data and generate brutal genz roasts.

GROUP INFO:
- name: {group_name}
- year: {year}
- total messages: {total_messages}
- total participants: {total_participants}
- chat type: {chat_type}

TOP WORDS USED IN CHAT (USE THESE FOR ROASTING):
{top_words}

MEMBER STATS:
{member_stats}

GROUP VIBES:
- peak hour: {peak_hour}:00
- topics they talk about: {topics}

generate a JSON response:
1. "brainrot_score": number 0-100 rating how chronically online this group is
2. "group_roast": ONE single string, max 2-3 lines, brutal roast about the group/chat. use their actual words and topics against them. if 2 person chat roast the situationship energy hard.
3. "individual_roasts": object with each persons name as key, value is ONE single string, max 2-3 lines, brutal roast about that person. USE THEIR SIGNATURE WORDS against them.

JSON format:
{{
  "brainrot_score": <number>,
  "group_roast": "short 2-3 line roast here",
  "individual_roasts": {{
    "PersonName": "short 2-3 line roast here",
    ...
  }}
}}

IMPORTANT:
- no emojis ever
- all lowercase
- no em dashes, use commas instead
- NO NUMBERS OR STATS in roasts, dont mention message counts or any statistics
- keep it SHORT, max 2-3 lines per roast, punchy and devastating
- base roasts on their TOP WORDS and SIGNATURE WORDS not generic personality traits
- reference specific names topics and words from their actual chats
- make each roast unique and specific to that person/group"""


def build_member_stats_context(
    top_chatters: dict,
    signature_words: dict,
    personality_tags: dict,
    user_emojis: dict,
    night_owls: dict,
    early_birds: dict,
    double_texters: dict,
    response_times: dict,
    caps_users: dict,
    question_askers: dict,
    one_worders: dict,
    sample_messages: dict = None,
) -> str:
    """Build context string for each member"""
    lines = []

    for i, (person, msg_count) in enumerate(top_chatters.items(), 1):
        person_lines = [f"\n{i}. {person}:"]
        person_lines.append(f"   - Messages: {msg_count} (#{i} in group)")

        # Signature words
        if person in signature_words and signature_words[person]:
            words = signature_words[person]
            if isinstance(words, list):
                person_lines.append(f"   - Signature words: {', '.join(words[:5])}")
            elif isinstance(words, str):
                person_lines.append(f"   - Signature words: {words}")

        # Personality tags
        if person in personality_tags and personality_tags[person]:
            tags = [t['tag'] for t in personality_tags[person][:4]]
            person_lines.append(f"   - Personality: {', '.join(tags)}")

        # Top emojis
        if person in user_emojis:
            emoji_data = user_emojis[person]
            if isinstance(emoji_data, dict) and 'top' in emoji_data:
                emojis = list(emoji_data['top'].keys())[:3]
                if emojis:
                    person_lines.append(f"   - Fav emojis: {' '.join(emojis)}")

        # Night owl / Early bird
        if person in night_owls and night_owls[person] > 10:
            person_lines.append(f"   - Night owl: {night_owls[person]} late night msgs")
        elif person in early_birds and early_birds[person] > 5:
            person_lines.append(f"   - Early bird: {early_birds[person]} morning msgs")

        # Double texter
        if person in double_texters and double_texters[person] > 10:
            person_lines.append(f"   - Double texter: {double_texters[person]} times")

        # Response time
        if person in response_times:
            rt = response_times[person]
            if isinstance(rt, dict) and 'avg_seconds' in rt:
                avg = rt['avg_seconds']
                if avg < 60:
                    person_lines.append(f"   - Replies in: ~{int(avg)}s (instant)")
                elif avg < 300:
                    person_lines.append(f"   - Replies in: ~{int(avg/60)}min")
                else:
                    person_lines.append(f"   - Replies in: ~{int(avg/60)}min (slow)")

        # Caps user
        if person in caps_users:
            caps = caps_users[person]
            if isinstance(caps, dict) and caps.get('caps_messages', 0) > 5:
                person_lines.append(f"   - CAPS LOCK USER: {caps['caps_messages']} shouty msgs")

        # Question asker
        if person in question_askers:
            qa = question_askers[person]
            if isinstance(qa, dict) and qa.get('questions', 0) > 10:
                person_lines.append(f"   - Question asker: {qa['questions']} questions")

        # One worder
        if person in one_worders:
            ow = one_worders[person]
            if isinstance(ow, dict) and ow.get('rate', 0) > 20:
                person_lines.append(f"   - One-word replies: {ow['rate']}% of msgs")

        # Sample messages (actual things they said)
        if sample_messages and person in sample_messages:
            msgs = sample_messages[person]
            if msgs:
                person_lines.append(f"   - Sample messages they sent:")
                for msg in msgs[:8]:
                    person_lines.append(f"     \"{msg}\"")

        lines.extend(person_lines)

    return '\n'.join(lines)


def build_roast_prompt(
    group_name: str,
    year: int,
    total_messages: int,
    total_participants: int,
    peak_hour: int,
    topics: list,
    top_words: list,
    member_stats_context: str,
    member_names: list = None,
) -> str:
    """Build the full user prompt"""

    # Format top words (word: count)
    top_words_str = ', '.join([f"{w[0]}({w[1]})" for w in top_words[:30]]) if top_words else "none"

    # Format topics
    topics_str = ', '.join(topics[:4]) if topics else "random chaos"

    # Determine chat type
    if total_participants == 2:
        names = member_names or ["Person1", "Person2"]
        chat_type = f"2 PERSON PRIVATE CHAT between {names[0]} and {names[1]}, this is likely a situationship or dating scenario, roast whos more down bad, whos carrying the convo, whos clearly trying harder, be brutal about the relationship dynamics"
    elif total_participants <= 5:
        chat_type = "small friend group chat"
    else:
        chat_type = "large group chat"

    return ROAST_USER_PROMPT.format(
        group_name=group_name or "unnamed group",
        year=year,
        total_messages=total_messages,
        total_participants=total_participants,
        chat_type=chat_type,
        peak_hour=peak_hour if peak_hour else "unknown",
        topics=topics_str,
        top_words=top_words_str,
        member_stats=member_stats_context,
    )
