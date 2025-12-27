"""
OpenAI service for AI-powered roasts
"""

import json
import logging
import os
from openai import OpenAI

from .prompts import ROAST_SYSTEM_PROMPT, build_member_stats_context, build_roast_prompt

logger = logging.getLogger(__name__)


def get_openai_client():
    """Get OpenAI client"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    return OpenAI(api_key=api_key)


def generate_roasts(
    group_name: str,
    year: int,
    total_messages: int,
    total_participants: int,
    peak_hour: int,
    topics: list,
    top_words: list,
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
) -> dict:
    """
    Generate AI-powered roasts using OpenAI GPT-4o-mini

    Returns:
        {
            "brainrot_score": int,
            "group_roast": str,
            "individual_roasts": dict[str, str]
        }
    """
    try:
        client = get_openai_client()

        # Build member stats context
        member_stats_context = build_member_stats_context(
            top_chatters=top_chatters,
            signature_words=signature_words,
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

        # Build prompt
        member_names = list(top_chatters.keys())
        user_prompt = build_roast_prompt(
            group_name=group_name,
            year=year,
            total_messages=total_messages,
            total_participants=total_participants,
            peak_hour=peak_hour,
            topics=topics,
            top_words=top_words,
            member_stats_context=member_stats_context,
            member_names=member_names,
        )

        logger.info(f"Calling OpenAI for roasts (group: {group_name}, {total_participants} members)")

        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": ROAST_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.9,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        # Parse response
        content = response.choices[0].message.content
        result = json.loads(content)

        # Validate structure
        if "brainrot_score" not in result:
            result["brainrot_score"] = 69  # default meme number

        if "group_roast" not in result:
            result["group_roast"] = "this group is too mid to roast fr"

        if "individual_roasts" not in result:
            result["individual_roasts"] = {}

        # Ensure brainrot_score is int
        result["brainrot_score"] = int(result["brainrot_score"])

        # Ensure group_roast is a string (in case AI returns array)
        if isinstance(result["group_roast"], list):
            result["group_roast"] = " ".join(result["group_roast"])

        # Ensure individual roasts are strings (in case AI returns arrays)
        for person, roast in result["individual_roasts"].items():
            if isinstance(roast, list):
                result["individual_roasts"][person] = " ".join(roast)

        logger.info(f"Generated roasts successfully (brainrot_score: {result['brainrot_score']})")

        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response as JSON: {e}")
        return _fallback_roasts(top_chatters)

    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return _fallback_roasts(top_chatters)


def _fallback_roasts(top_chatters: dict) -> dict:
    """Fallback roasts if OpenAI fails"""
    return {
        "brainrot_score": 50,
        "group_roast": "this group exists and thats already concerning fr fr. collective screen time here could power a city no cap. touch grass challenge impossible edition. the wifi password saw this chat and changed itself",
        "individual_roasts": {
            person: "has a phone and uses it unfortunately. contributes to the chaos. is here for some reason"
            for person in list(top_chatters.keys())[:10]
        },
    }
