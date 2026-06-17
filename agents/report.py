from agents.skill_gap import SkillGapReport


def generate_report(report: SkillGapReport) -> str:
    lines = [
        "# Raport Skill Gap",
        "",
        f"**Podsumowanie:** {report.summary}",
        "",
        "## Najczęściej brakujące umiejętności",
        "",
    ]
    for s in report.top_missing_skills:
        lines.append(f"- {s}")

    lines += ["", "## Ranking ofert", ""]

    for m in sorted(report.offer_matches, key=lambda x: x.match_score, reverse=True):
        icon = "✅" if m.match_score >= 50 else "⚠️"
        lines.append(f"### {icon} {m.title} @ {m.company} — {m.match_score}%")
        lines.append(f"_{m.comment}_")
        if m.matched_skills:
            lines.append(f"- Dopasowane: {', '.join(m.matched_skills)}")
        if m.missing_skills:
            lines.append(f"- Brakuje: {', '.join(m.missing_skills)}")
        lines.append("")

    lines.append("---")
    lines.append(f"_Wygenerowano automatycznie przez Job Scout Agent_")
    return "\n".join(lines)
