from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer

from models.offer import JobOffer

COLLECTION_NAME = "job_offers"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_SIZE = 384
SIMILARITY_THRESHOLD = 0.92

_client: QdrantClient | None = None
_encoder: SentenceTransformer | None = None


def _get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient("localhost", port=6333)
    return _client


def _get_encoder() -> SentenceTransformer:
    global _encoder
    if _encoder is None:
        _encoder = SentenceTransformer(EMBEDDING_MODEL)
    return _encoder


def _offer_text(offer: JobOffer) -> str:
    parts = [offer.title]
    if offer.company:
        parts.append(offer.company)
    if offer.city:
        parts.append(offer.city)
    parts.extend(s.name for s in offer.required_skills)
    return " | ".join(parts)


def init_collection():
    client = _get_client()
    collections = client.get_collections().collections
    if not any(c.name == COLLECTION_NAME for c in collections):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        print(f"  ✓ Kolekcja '{COLLECTION_NAME}' utworzona w Qdrant")


def is_duplicate(offer: JobOffer) -> bool:
    client = _get_client()
    encoder = _get_encoder()
    text = _offer_text(offer)
    vector = encoder.encode(text).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=1,
        score_threshold=SIMILARITY_THRESHOLD,
    )
    return len(results.points) > 0


def index_offer(offer: JobOffer):
    client = _get_client()
    encoder = _get_encoder()
    text = _offer_text(offer)
    vector = encoder.encode(text).tolist()

    payload = {
        "title": offer.title,
        "company": offer.company,
        "city": offer.city,
        "url": offer.url,
        "required_skills": [s.name for s in offer.required_skills],
    }

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(id=hash(text) % (2**63), vector=vector, payload=payload)
        ],
    )


def filter_new_offers(offers: list[JobOffer]) -> list[JobOffer]:
    new_offers: list[JobOffer] = []
    duplicates = 0
    for offer in offers:
        if is_duplicate(offer):
            duplicates += 1
        else:
            index_offer(offer)
            new_offers.append(offer)

    if duplicates:
        print(f"  ✓ Odrzucono {duplicates} duplikatów")
    return new_offers
