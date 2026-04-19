from typing import List, Optional
import math


# Scoring weights (must sum to 100)
WEIGHTS = {
    "skills": 40,
    "experience": 25,
    "education": 10,
    "industry": 10,
    "certifications": 10,
    "location": 5,
}

EDUCATION_RANK = {
    "phd": 5,
    "masters": 4,
    "bachelors": 3,
    "diploma": 2,
    "unknown": 1,
}

PREMIUM_INSTITUTIONS = ["iit", "iim", "nit", "bits", "mit", "stanford", "oxford", "harvard", "cambridge", "cmu"]

CERT_KEYWORDS = ["aws certified", "cka", "ckad", "google cloud", "azure certified", "pmp", "scrum master", "cissp", "gcp", "kubernetes"]


def score_skills(candidate_skills: List[str], required_skills: List[str], priority_skills: List[str]) -> dict:
    """Score skill match with priority weighting."""
    if not required_skills:
        return {"score": 50, "matched": [], "missing": [], "bonus": []}

    cand_lower = [s.lower() for s in (candidate_skills or [])]
    req_lower = [s.lower() for s in required_skills]
    priority_lower = [s.lower() for s in (priority_skills or [])]

    matched = [s for s in req_lower if s in cand_lower]
    missing = [s for s in req_lower if s not in cand_lower]
    
    # Priority skill bonus: worth 1.5x
    priority_matched = [s for s in priority_lower if s in cand_lower]
    priority_missing = [s for s in priority_lower if s not in cand_lower]

    base_score = len(matched) / len(req_lower) if req_lower else 0

    # Priority multiplier
    if priority_lower:
        priority_ratio = len(priority_matched) / len(priority_lower)
        score = (base_score * 0.6 + priority_ratio * 0.4) * 100
    else:
        score = base_score * 100

    # Bonus skills candidate has beyond requirements
    bonus = [s for s in cand_lower if s not in req_lower]

    return {
        "score": round(min(score, 100), 1),
        "matched": matched,
        "missing": missing,
        "priority_matched": priority_matched,
        "priority_missing": priority_missing,
        "bonus": bonus[:10],  # top 10 bonus skills
    }


def score_experience(years_exp: float, exp_min: int, exp_max: int) -> float:
    """Score experience fit. Sweet spot = max score."""
    if years_exp <= 0:
        return 10.0

    if exp_min <= years_exp <= exp_max:
        # In range - full score, slight bonus for hitting middle
        mid = (exp_min + exp_max) / 2
        distance = abs(years_exp - mid) / max(exp_max - exp_min, 1)
        return round(90 + (1 - distance) * 10, 1)
    elif years_exp < exp_min:
        # Under-experienced
        ratio = years_exp / max(exp_min, 1)
        return round(max(ratio * 70, 20), 1)
    else:
        # Over-experienced (may decline offer)
        excess = years_exp - exp_max
        penalty = min(excess * 5, 30)
        return round(max(100 - penalty, 60), 1)


def score_education(education_level: str, required_education: Optional[str], institution: str) -> float:
    """Score education fit."""
    candidate_rank = EDUCATION_RANK.get(education_level, 1)
    
    # Default required: bachelors
    required_level = "bachelors"
    if required_education:
        for lvl in EDUCATION_RANK:
            if lvl in required_education.lower():
                required_level = lvl
                break
    
    required_rank = EDUCATION_RANK.get(required_level, 3)
    
    if candidate_rank >= required_rank:
        base = 80
        # Premium institution bonus
        inst_lower = (institution or "").lower()
        if any(p in inst_lower for p in PREMIUM_INSTITUTIONS):
            base = 100
        elif candidate_rank > required_rank:
            base = 90
        return float(base)
    else:
        gap = required_rank - candidate_rank
        return max(80 - gap * 20, 20)


def score_certifications(skills: List[str], text_snippet: str = "") -> float:
    """Score certifications."""
    all_text = " ".join(skills or []).lower() + " " + text_snippet.lower()
    cert_count = sum(1 for cert in CERT_KEYWORDS if cert in all_text)
    if cert_count == 0:
        return 30.0
    return min(30 + cert_count * 25, 100)


def score_location(candidate_location: str, job_location: str) -> float:
    """Score location compatibility."""
    if not job_location or not candidate_location:
        return 70.0

    job_loc_lower = job_location.lower()
    cand_loc_lower = candidate_location.lower()

    if "remote" in job_loc_lower or "anywhere" in job_loc_lower:
        return 100.0
    
    # Same city
    job_city = job_loc_lower.split(",")[0].strip()
    cand_city = cand_loc_lower.split(",")[0].strip()
    
    if job_city in cand_loc_lower or cand_city in job_loc_lower:
        return 100.0
    
    # Same country-region heuristic
    return 50.0


def calculate_overall_score(
    candidate_skills: List[str],
    required_skills: List[str],
    priority_skills: List[str],
    years_experience: float,
    exp_min: int,
    exp_max: int,
    education_level: str,
    required_education: str,
    education_institution: str,
    candidate_location: str,
    job_location: str,
    raw_text: str = "",
) -> dict:
    """Full scoring pipeline. Returns weighted overall + breakdown."""

    skill_result = score_skills(candidate_skills, required_skills, priority_skills)
    exp_score = score_experience(years_experience, exp_min, exp_max)
    edu_score = score_education(education_level, required_education, education_institution)
    cert_score = score_certifications(candidate_skills, raw_text)
    loc_score = score_location(candidate_location, job_location)

    # Industry score: proxy via skill domain overlap
    industry_score = min(skill_result["score"] * 0.8 + 20, 100)

    overall = (
        skill_result["score"] * WEIGHTS["skills"] / 100 +
        exp_score * WEIGHTS["experience"] / 100 +
        edu_score * WEIGHTS["education"] / 100 +
        industry_score * WEIGHTS["industry"] / 100 +
        cert_score * WEIGHTS["certifications"] / 100 +
        loc_score * WEIGHTS["location"] / 100
    )

    return {
        "overall_score": round(overall, 1),
        "skill_score": round(skill_result["score"], 1),
        "experience_score": round(exp_score, 1),
        "education_score": round(edu_score, 1),
        "industry_score": round(industry_score, 1),
        "certification_score": round(cert_score, 1),
        "location_score": round(loc_score, 1),
        "matched_skills": skill_result["matched"],
        "missing_skills": skill_result["missing"],
        "priority_matched": skill_result.get("priority_matched", []),
        "priority_missing": skill_result.get("priority_missing", []),
        "bonus_skills": skill_result["bonus"],
    }


def generate_ai_summary(candidate: dict) -> str:
    """Rule-based one-line candidate summary."""
    name = candidate.get("full_name", "Candidate")
    years = candidate.get("years_experience", 0)
    role = candidate.get("current_title", "professional")
    company = candidate.get("current_company", "")
    skills = candidate.get("skills", [])[:3]
    
    skill_str = " + ".join(skills) if skills else "varied skills"
    company_str = f" at {company}" if company else ""
    
    seniority = "Senior" if years >= 6 else "Mid-level" if years >= 3 else "Junior"
    
    return f"{years:.0f}-year {seniority.lower()} {role}{company_str} with strong {skill_str} background."


def generate_fit_explanation(scores: dict, candidate: dict, job: dict) -> str:
    """Explain why a candidate got their score."""
    overall = scores["overall_score"]
    matched = scores.get("matched_skills", [])
    missing = scores.get("missing_skills", [])
    
    lines = [f"Scored {overall}/100 because: "]
    
    if scores["skill_score"] >= 80:
        lines.append(f"strong skill match ({', '.join(matched[:3])})")
    elif scores["skill_score"] >= 50:
        lines.append(f"partial skill match ({len(matched)} of {len(matched)+len(missing)} required skills)")
    else:
        lines.append(f"weak skill match — missing {', '.join(missing[:3])}")
    
    years = candidate.get("years_experience", 0)
    exp_min = job.get("experience_min", 0)
    exp_max = job.get("experience_max", 10)
    
    if exp_min <= years <= exp_max:
        lines.append(f"{years:.0f} yrs experience in target range ({exp_min}-{exp_max})")
    elif years > exp_max:
        lines.append(f"over-experienced ({years:.0f} yrs vs {exp_max} max)")
    else:
        lines.append(f"under-experienced ({years:.0f} yrs vs {exp_min} min)")
    
    edu = candidate.get("education_institution", "")
    if edu:
        lines.append(f"educated at {edu}")
    
    if missing:
        lines.append(f"Missing: {', '.join(missing[:3])}")
    
    return ". ".join(lines) + "."


def calculate_trainability_score(scores: dict, years_experience: float) -> float:
    """Score how trainable a candidate is for missing skills."""
    missing_penalty = len(scores.get("missing_skills", [])) * 8
    base = max(scores["overall_score"] - missing_penalty + 20, 0)
    
    # Junior candidates more trainable
    if years_experience < 4:
        base = min(base + 15, 100)
    
    return round(min(base, 100), 1)


def rank_candidates(candidates: list) -> list:
    """Rank candidates by overall score, apply tiebreaking."""
    sorted_cands = sorted(
        candidates,
        key=lambda c: (
            c.get("overall_score", 0),
            c.get("skill_score", 0),
            c.get("years_experience", 0),
        ),
        reverse=True
    )
    for i, c in enumerate(sorted_cands):
        c["rank_position"] = i + 1
    return sorted_cands
