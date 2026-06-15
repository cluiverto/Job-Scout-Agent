import json
from pathlib import Path

from pydantic import BaseModel

from agents.base import create_agent
from storage import load_offers


class OfferMatch(BaseModel):
    title: str
    company: str
    match_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    comment: str


class SkillGapReport(BaseModel):
    top_missing_skills: list[str]
    offer_matches: list[OfferMatch]
    summary: str


agent = create_agent(
    output_type=SkillGapReport,
    system_prompt=(
        "Jesteś analitykiem rynku pracy. "
        "Porównujesz umiejętności użytkownika z wymaganiami w ofertach pracy. "
        "Bądź szczery i praktyczny — jeśli brakuje kluczowych umiejętności, powiedz to wprost. "
        "match_score to liczba 0-100. "
        "W comment napisz krótką opinię dlaczego oferta pasuje lub nie."
    ),
)


def run_analysis(profile_path: str = "profile.json") -> SkillGapReport:
    profile = json.loads(Path(profile_path).read_text(encoding="utf-8"))
    user_skills = profile["skills"]

    offers = load_offers()
    if not offers:
        raise RuntimeError("Brak ofert. Uruchom najpierw scraper.")

    offers_text = json.dumps(
        [
            {
                "title": o.title,
                "company": o.company,
                "required_skills": [s.name for s in o.required_skills],
                "nice_to_have": [s.name for s in o.nice_to_have_skills],
                "description": o.description[:500] if o.description else "",
            }
            for o in offers
        ],
        ensure_ascii=False,
        indent=2,
    )

    result = agent.run_sync(
        f"Umiejętności użytkownika: {', '.join(user_skills)}\n\n"
        f"Oferty:\n{offers_text}"
    )
    return result.output


def main():
    report = run_analysis()
    print("# Analiza Skill Gap (AI)\n")
    print(f"**Podsumowanie:** {report.summary}\n")
    print("**Najczęściej brakujące umiejętności:**")
    for s in report.top_missing_skills:
        print(f"  - {s}")
    print("\n## Ranking ofert\n")
    for m in report.offer_matches:
        icon = "✅" if m.match_score >= 50 else "⚠️"
        print(f"{icon} **{m.match_score}%** — {m.title} @ {m.company}")
        print(f"   {m.comment}")
        if m.missing_skills:
            print(f"   Brakuje: {', '.join(m.missing_skills)}")
        print()


if __name__ == "__main__":
    main()
