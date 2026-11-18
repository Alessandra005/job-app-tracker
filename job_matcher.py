def normalize_skills(skills):
    """Convert skills into a consistent format for comparison."""
    return {
        skill.strip().lower()
        for skill in skills
        if skill.strip()
    }


def calculate_job_match(user_skills, requirements, ai_equivalencies=None):
    """
    Compare user skills with a job's requirements.

    Required skills contribute 70%.
    Preferred skills contribute 30%.
    """

    if not requirements:
        return None

    required = requirements.get("required_skills", [])
    preferred = requirements.get("preferred_skills", [])

    user_skills = normalize_skills(user_skills)
    equivalent_skills = normalize_skills(ai_equivalencies or [])
    user_skills.update(equivalent_skills)

    required_skills = normalize_skills(required)
    preferred_skills = normalize_skills(preferred)

    if not required_skills and not preferred_skills:
        return None

    matched_required = user_skills & required_skills
    matched_preferred = user_skills & preferred_skills

    missing_required = required_skills - user_skills
    missing_preferred = preferred_skills - user_skills

    required_score = (
        len(matched_required) / len(required_skills)
        if required_skills else 1
    )

    preferred_score = (
        len(matched_preferred) / len(preferred_skills)
        if preferred_skills else 1
    )

    score = (required_score * 0.70 + preferred_score * 0.30) * 100

    return {
        "match_percentage": round(score),
        "matched_required": sorted(matched_required),
        "matched_preferred": sorted(matched_preferred),
        "missing_required": sorted(missing_required),
        "missing_preferred": sorted(missing_preferred)
    }
