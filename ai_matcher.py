
import os
import json
import logging

from dotenv import load_dotenv
from google import genai

load_dotenv()

logging.basicConfig(level=logging.INFO)

def get_skill_equivalencies(user_skills, job_skills):
    """Identify direct skill equivalencies using Gemini."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or not user_skills or not job_skills:
        return []

    client = genai.Client(api_key=api_key)

    prompt = f"""
    Identify direct technical skill equivalencies.

    USER SKILLS:
    {json.dumps(user_skills)}

    JOB SKILLS:
    {json.dumps(job_skills)}

    Rules:
    1. Only use skills from the supplied lists.
    2. Do not invent user skills.
    3. Do not include exact matches.
    4. Only identify genuine, direct equivalencies.
    5. Do not treat broadly related skills as equivalent.

    Return only JSON:
    {{
        "equivalencies": [
            {{
                "user_skill": "PostgreSQL",
                "job_skill": "SQL"
            }}
        ]
    }}

    Return an empty list if there are no equivalencies.
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )

        result = json.loads(response.text)

        valid_matches = []
        seen = set()

        user_lookup = {s.strip().casefold() for s in user_skills}
        job_lookup = {s.strip().casefold() for s in job_skills}

        for item in result.get("equivalencies", []):
            if not isinstance(item, dict):
                continue

            user_skill = item.get("user_skill")
            job_skill = item.get("job_skill")

            if not isinstance(user_skill, str) or not isinstance(job_skill, str):
                continue

            user_skill = user_skill.strip()
            job_skill = job_skill.strip()

            pair = (user_skill.casefold(), job_skill.casefold())

            if (
                user_skill.casefold() in user_lookup
                and job_skill.casefold() in job_lookup
                and user_skill.casefold() != job_skill.casefold()
                and pair not in seen
            ):
                valid_matches.append({
                    "user_skill": user_skill,
                    "job_skill": job_skill
                })
                seen.add(pair)

        return valid_matches

    except Exception:
        logging.exception("Gemini skill matching failed.")
        return []
