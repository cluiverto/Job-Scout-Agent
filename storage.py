import json
from pathlib import Path
from models.offer import JobOffer


DEFAULT_PATH = Path("data/offers.json")


def save_offers(offers: list[JobOffer], path: str | Path = DEFAULT_PATH) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [o.model_dump() for o in offers]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_offers(path: str | Path = DEFAULT_PATH) -> list[JobOffer]:
    path = Path(path)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [JobOffer.model_validate(o) for o in data]
