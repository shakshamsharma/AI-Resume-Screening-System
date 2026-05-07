"""
AI Evaluator Service - Uses LLM to evaluate candidates based on structured data.
AI acts as EVALUATOR, not EXTRACTOR.
"""
import os
from typing import Dict, Any, List, Optional
import json


def get_ai_client():
    """Get AI client based on available API keys."""
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if openai_key:
        try:
            from openai import OpenAI
            return OpenAI(api_key=openai_key), "openai"
        except ImportError:
            pass
    
    if anthropic_key:
        try:
            from anthropic import Anthropic
            return Anthropic(api_key=anthropic_key), "anthropic"
        except ImportError:
            pass
    
    return None, None


def generate_ai_summary(
    candidate: Dict[str, Any],
    job: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate AI-powered candidate summary.
    Falls back to rule-based if AI is unavailable.
    """
    client, provider = get_ai_client()
    
    if not client:
        return _generate_rule_based_summary(candidate)
    
    # Prepare structured data for AI
    candidate_data = {
        "name": candidate.get("full_name", "Unknown"),
        "years_experience": candidate.get("years_experience", 0),
        "current_role": candidate.get("current_role") or candidate.get("current_title"),
        "current_company": candidate.get("current_company"),
        "skills": candidate.get("skills", [])[:10],  # Top 10 skills
        "education": {
            "level": candidate.get("education_level"),
            "institution": candidate.get("education_institution"),
        },
        "certifications": candidate.get("certifications", []),
    }
    
    prompt = f"""You are a professional recruiter. Generate a concise, professional one-line summary of this candidate.

Candidate Data (STRUCTURED - DO NOT INVENT):
{json.dumps(candidate_data, indent=2)}

Requirements:
- One sentence only (max 25 words)
- Focus on experience level, key skills, and current role
- Be factual and professional
- DO NOT invent information not in the data
- If experience is 0, mention "fresher" or "entry-level"

Example formats:
- "5-year senior backend engineer at TechCorp with strong Python, AWS, and microservices background."
- "Fresher with B.Tech in CS, skilled in React, Node.js, and MongoDB."
- "Mid-level data scientist with 3 years experience in ML, Python, and TensorFlow."

Generate summary:"""
    
    try:
        if provider == "openai":
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100,
            )
            return response.choices[0].message.content.strip()
        
        elif provider == "anthropic":
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()
    
    except Exception as e:
        print(f"AI summary generation failed: {e}")
        return _generate_rule_based_summary(candidate)
    
    return _generate_rule_based_summary(candidate)


def generate_fit_explanation(
    scores: Dict[str, Any],
    candidate: Dict[str, Any],
    job: Dict[str, Any],
) -> str:
    """
    Generate AI-powered explanation of candidate-job fit.
    Falls back to rule-based if AI unavailable.
    """
    client, provider = get_ai_client()
    
    if not client:
        return _generate_rule_based_fit_explanation(scores, candidate, job)
    
    # Prepare structured data
    evaluation_data = {
        "overall_score": scores.get("overall_score", 0),
        "skill_score": scores.get("skill_score", 0),
        "experience_score": scores.get("experience_score", 0),
        "matched_skills": scores.get("matched_skills", [])[:5],
        "missing_skills": scores.get("missing_skills", [])[:5],
        "priority_matched": scores.get("priority_matched", []),
        "priority_missing": scores.get("priority_missing", []),
        "candidate_experience": candidate.get("years_experience", 0),
        "required_experience": f"{job.get('experience_min', 0)}-{job.get('experience_max', 10)} years",
        "education_match": scores.get("education_score", 0) >= 80,
    }
    
    prompt = f"""You are a professional recruiter. Explain why this candidate received their match score.

Evaluation Data (FACTUAL - DO NOT INVENT):
{json.dumps(evaluation_data, indent=2)}

Job Title: {job.get('title', 'Unknown')}

Requirements:
- 2-3 sentences maximum
- Explain the score based on the data
- Mention key strengths and gaps
- Be specific about matched/missing skills
- Be honest about experience fit
- Professional and constructive tone

Example formats:
- "Scored 85/100 due to strong skill match (Python, AWS, Docker) and 6 years experience in target range (5-8). Missing SQL and Kubernetes but has strong fundamentals."
- "Scored 62/100 because partial skill match (3 of 6 required skills) and under-experienced (2 yrs vs 5 min). Strong in React and TypeScript but missing backend skills."

Generate explanation:"""
    
    try:
        if provider == "openai":
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150,
            )
            return response.choices[0].message.content.strip()
        
        elif provider == "anthropic":
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()
    
    except Exception as e:
        print(f"AI fit explanation failed: {e}")
        return _generate_rule_based_fit_explanation(scores, candidate, job)
    
    return _generate_rule_based_fit_explanation(scores, candidate, job)


def generate_hiring_recommendation(
    scores: Dict[str, Any],
    candidate: Dict[str, Any],
    job: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate AI-powered hiring recommendation.
    Returns: {
        "recommendation": "strong_yes" | "yes" | "maybe" | "no",
        "reasoning": str,
        "key_strengths": List[str],
        "key_concerns": List[str],
        "interview_focus_areas": List[str],
    }
    """
    client, provider = get_ai_client()
    
    if not client:
        return _generate_rule_based_recommendation(scores, candidate, job)
    
    # Prepare comprehensive data
    analysis_data = {
        "scores": {
            "overall": scores.get("overall_score", 0),
            "skills": scores.get("skill_score", 0),
            "experience": scores.get("experience_score", 0),
            "education": scores.get("education_score", 0),
        },
        "matched_skills": scores.get("matched_skills", []),
        "missing_skills": scores.get("missing_skills", []),
        "priority_matched": scores.get("priority_matched", []),
        "priority_missing": scores.get("priority_missing", []),
        "bonus_skills": scores.get("bonus_skills", [])[:5],
        "candidate": {
            "experience_years": candidate.get("years_experience", 0),
            "education": candidate.get("education_level"),
            "institution": candidate.get("education_institution"),
            "certifications": candidate.get("certifications", []),
        },
        "job_requirements": {
            "title": job.get("title"),
            "experience_range": f"{job.get('experience_min', 0)}-{job.get('experience_max', 10)} years",
            "required_skills": job.get("required_skills", []),
            "priority_skills": job.get("priority_skills", []),
        }
    }
    
    prompt = f"""You are a senior technical recruiter. Provide a hiring recommendation for this candidate.

Analysis Data (FACTUAL):
{json.dumps(analysis_data, indent=2)}

Provide your recommendation in JSON format:
{{
  "recommendation": "strong_yes" | "yes" | "maybe" | "no",
  "reasoning": "2-3 sentence explanation",
  "key_strengths": ["strength1", "strength2", "strength3"],
  "key_concerns": ["concern1", "concern2"],
  "interview_focus_areas": ["area1", "area2", "area3"]
}}

Guidelines:
- "strong_yes": 85+ score, all priority skills, experience perfect fit
- "yes": 70-84 score, most skills matched, minor gaps trainable
- "maybe": 55-69 score, significant gaps but potential
- "no": <55 score, major skill/experience gaps

Be honest and data-driven. Only return valid JSON."""
    
    try:
        if provider == "openai":
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=400,
                response_format={"type": "json_object"},
            )
            result = json.loads(response.choices[0].message.content)
            return result
        
        elif provider == "anthropic":
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=400,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )
            # Parse JSON from response
            text = response.content[0].text.strip()
            # Extract JSON if wrapped in markdown
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            result = json.loads(text)
            return result
    
    except Exception as e:
        print(f"AI recommendation failed: {e}")
        return _generate_rule_based_recommendation(scores, candidate, job)
    
    return _generate_rule_based_recommendation(scores, candidate, job)


# ═══════════════════════════════════════════════════════════════════════════
# RULE-BASED FALLBACKS
# ═══════════════════════════════════════════════════════════════════════════

def _generate_rule_based_summary(candidate: Dict[str, Any]) -> str:
    """Rule-based candidate summary (fallback)."""
    name = candidate.get("full_name", "Candidate")
    years = candidate.get("years_experience", 0)
    role = candidate.get("current_role") or candidate.get("current_title") or "professional"
    company = candidate.get("current_company", "")
    skills = candidate.get("skills", [])[:3]
    
    if years == 0:
        seniority = "Fresher"
        exp_str = "entry-level"
    elif years < 3:
        seniority = "Junior"
        exp_str = f"{years:.0f}-year"
    elif years < 6:
        seniority = "Mid-level"
        exp_str = f"{years:.0f}-year"
    else:
        seniority = "Senior"
        exp_str = f"{years:.0f}-year"
    
    skill_str = ", ".join(skills) if skills else "varied skills"
    company_str = f" at {company}" if company else ""
    
    return f"{exp_str} {seniority.lower()} {role}{company_str} with {skill_str} background."


def _generate_rule_based_fit_explanation(
    scores: Dict[str, Any],
    candidate: Dict[str, Any],
    job: Dict[str, Any],
) -> str:
    """Rule-based fit explanation (fallback)."""
    overall = scores.get("overall_score", 0)
    matched = scores.get("matched_skills", [])
    missing = scores.get("missing_skills", [])
    years = candidate.get("years_experience", 0)
    exp_min = job.get("experience_min", 0)
    exp_max = job.get("experience_max", 10)
    
    parts = [f"Scored {overall:.0f}/100 because:"]
    
    # Skills assessment
    if scores.get("skill_score", 0) >= 80:
        parts.append(f"strong skill match ({', '.join(matched[:3])})")
    elif scores.get("skill_score", 0) >= 50:
        parts.append(f"partial skill match ({len(matched)} of {len(matched)+len(missing)} required)")
    else:
        parts.append(f"weak skill match, missing {', '.join(missing[:3])}")
    
    # Experience assessment
    if exp_min <= years <= exp_max:
        parts.append(f"{years:.0f} yrs in range ({exp_min}-{exp_max})")
    elif years > exp_max:
        parts.append(f"over-experienced ({years:.0f} yrs vs {exp_max} max)")
    elif years > 0:
        parts.append(f"under-experienced ({years:.0f} yrs vs {exp_min} min)")
    else:
        parts.append("fresher (0 years experience)")
    
    # Education
    edu = candidate.get("education_institution", "")
    if edu:
        parts.append(f"educated at {edu}")
    
    return ". ".join(parts) + "."


def _generate_rule_based_recommendation(
    scores: Dict[str, Any],
    candidate: Dict[str, Any],
    job: Dict[str, Any],
) -> Dict[str, Any]:
    """Rule-based hiring recommendation (fallback)."""
    overall = scores.get("overall_score", 0)
    skill_score = scores.get("skill_score", 0)
    matched = scores.get("matched_skills", [])
    missing = scores.get("missing_skills", [])
    priority_missing = scores.get("priority_missing", [])
    
    # Determine recommendation
    if overall >= 85 and not priority_missing:
        recommendation = "strong_yes"
        reasoning = "Excellent match with all priority skills and strong overall fit."
    elif overall >= 70:
        recommendation = "yes"
        reasoning = "Good match with most required skills. Minor gaps are trainable."
    elif overall >= 55:
        recommendation = "maybe"
        reasoning = "Moderate match with significant skill gaps but shows potential."
    else:
        recommendation = "no"
        reasoning = "Insufficient match due to major skill and experience gaps."
    
    # Key strengths
    strengths = []
    if skill_score >= 80:
        strengths.append(f"Strong skill match: {', '.join(matched[:3])}")
    if scores.get("experience_score", 0) >= 80:
        strengths.append("Experience level fits requirements perfectly")
    if scores.get("education_score", 0) >= 90:
        strengths.append(f"Premium education: {candidate.get('education_institution', '')}")
    if not strengths:
        strengths.append("Shows basic qualifications")
    
    # Key concerns
    concerns = []
    if missing:
        concerns.append(f"Missing skills: {', '.join(missing[:3])}")
    if priority_missing:
        concerns.append(f"Missing priority skills: {', '.join(priority_missing)}")
    if scores.get("experience_score", 0) < 60:
        concerns.append("Experience level doesn't match requirements")
    if not concerns:
        concerns.append("No major concerns identified")
    
    # Interview focus areas
    focus_areas = []
    if missing:
        focus_areas.append(f"Assess proficiency in: {', '.join(missing[:2])}")
    if candidate.get("years_experience", 0) < job.get("experience_min", 0):
        focus_areas.append("Evaluate learning ability and growth potential")
    focus_areas.append("Verify hands-on experience with matched skills")
    
    return {
        "recommendation": recommendation,
        "reasoning": reasoning,
        "key_strengths": strengths[:3],
        "key_concerns": concerns[:3],
        "interview_focus_areas": focus_areas[:3],
    }
