import httpx
from models.offer import JobOffer, Skill, SalaryRange
from storage import save_offers


BASE_URL = "https://justjoin.it"
API_URL = f"{BASE_URL}/api/candidate-api/offers"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": f"{BASE_URL}/job-offers/all-locations/ai",
    "Accept": "application/json",
}


def _parse_salary(employment_types: list[dict]) -> SalaryRange | None:
    for et in employment_types:
        if et.get("type") == "permanent":
            return SalaryRange(
                from_=et.get("from"),
                to=et.get("to"),
                currency=et.get("currency", "PLN"),
            )
    # fallback: first available
    if employment_types:
        et = employment_types[0]
        return SalaryRange(
            from_=et.get("from"),
            to=et.get("to"),
            currency=et.get("currency", "PLN"),
        )
    return None


def _parse_skills(skills: list[dict]) -> list[Skill]:
    return [Skill(name=s["name"], level=s.get("level")) for s in skills]


def _build_offer_url(slug: str) -> str:
    return f"{BASE_URL}/job-offer/{slug}"


def scrape_offers(
    category: str = "ai",
    max_pages: int = 3,
    valid_categories: set[str] | None = None,
) -> list[JobOffer]:
    if valid_categories is None:
        valid_categories = {"ai", "ml", "data"}

    offers: list[JobOffer] = []
    cursor = 0

    for page in range(max_pages):
        params = {}
        if cursor:
            params["cursor"] = cursor

        resp = httpx.get(API_URL, headers=HEADERS, params=params, timeout=15)
        resp.raise_for_status()
        body = resp.json()

        for item in body["data"]:
            item_cat = item.get("category", {}).get("key", "")
            if item_cat not in valid_categories:
                continue

            salary = _parse_salary(item.get("employmentTypes", []))
            url = _build_offer_url(item["slug"])

            offer = JobOffer(
                title=item["title"],
                company=item.get("companyName"),
                city=item.get("city"),
                salary=salary,
                experience_level=item.get("experienceLevel"),
                required_skills=_parse_skills(item.get("requiredSkills", [])),
                nice_to_have_skills=_parse_skills(item.get("niceToHaveSkills", [])),
                url=url,
            )

            # fetch description from detail endpoint
            try:
                detail_resp = httpx.get(
                    f"{API_URL}/{item['slug']}", headers=HEADERS, timeout=10
                )
                if detail_resp.status_code == 200:
                    detail = detail_resp.json()
                    offer.description = detail.get("body", "")
            except Exception:
                pass

            offers.append(offer)

        # pagination
        next_info = body.get("meta", {}).get("next", {})
        next_cursor = next_info.get("cursor")
        if next_cursor is None:
            break
        cursor = next_cursor

    return offers


if __name__ == "__main__":
    all_offers = scrape_offers(category="ai", max_pages=1)
    save_offers(all_offers)
    print(f"Found {len(all_offers)} offers → saved to data/offers.json")
    for o in all_offers[:3]:
        print(f"  - {o.title} @ {o.company} | {o.city}")
        print(f"    Skills: {[s.name for s in o.required_skills]}")
        print(f"    Salary: {o.salary}")
        print()
