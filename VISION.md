# Job Scout Agent — Wizja i Plan Rozwoju

## Cel

System agentowy, który scrapuje oferty pracy (justjoin.it + inne źródła),
analizuje trendy, porównuje wymagania z profilem użytkownika i wskazuje,
czego się uczyć + które oferty są najlepszym match'em.

Docelowo: agent, który znalazł pracę swojemu twórcy.

---

## Architektura docelowa

```
[Scrapers] → [Deduplikacja] → [Trend Analysis] → [Skill Gap] → [Match] → [Report]
     ↑              ↑                 ↑                 ↑            ↑           ↑
     │         Qdrant(embeddings)  Langfuse(trace)  Postgres(meta)  Redis(cache)
     └─── httpx + selectolax (async)
```

### Stack docelowy

| Warstwa | Technologia | Po co |
|---|---|---|
| Orchestracja | LangGraph | state machine, conditional edges, human-in-loop |
| Walidacja | Pydantic AI | typed agent outputs, nie json.loads |
| Scraping | httpx + selectolax | async, szybkie, mało zależności |
| Vector DB | Qdrant | deduplikacja ofert po embeddingach |
| Metadata DB | Postgres + SQLAlchemy async | oferty, analizy, ustawienia |
| Cache / Queue | Redis | cache embeddingów, kolejka zadań |
| API | FastAPI | endpoints dla UI i integracji |
| UI | Next.js | dashboard, raporty, konfiguracja |
| Scheduling | APScheduler | scrapowanie codziennie, analiza co tydzień |
| Observability | Langfuse | tracing, evals, debug agentów |
| Deployment | — | Azure/AWS/GCP (do ustalenia) |

### Przepływ danych (GraphState)

```python
raw_offers → deduplicated_offers → trend_report → skill_gaps → ranked_offers → final_report
```

Conditional edge: jeśli scraper znajdzie < 5 nowych ofert, pomiń trend analysis.

---

## MVP (Faza 0 — teraz, 1-2 tygodnie)

**Cel**: działający core, który można pokazać na GitHub i uruchomić lokalnie.

- [x] Scraper justjoin.it (httpx, proste parsowanie)
- [ ] GraphState + LangGraph (scrape → skill_gap → report)
- [ ] Skill Gap Agent (Pydantic AI: CV vs oferty)
- [ ] Report Agent (generuje raport MD)
- [ ] Storage: lokalny pickle/JSON (NA RAZIE)
- [ ] UI: brak (raport = plik MD)
- [ ] Deployment: brak

Uruchomienie: `python main.py` → dostajesz plik `raport.md`.

### Świadomie odłożone (nie zapomnij!):
- [ ] Qdrant (będzie w F1)
- [ ] Postgres (będzie w F1)
- [ ] Redis (będzie w F1)
- [ ] Trend Analysis Agent (będzie w F2)
- [ ] Match Agent z scoringiem (będzie w F2)
- [ ] FastAPI (będzie w F2)
- [ ] Next.js dashboard (będzie w F3)
- [ ] Langfuse full tracing (będzie w F2)
- [ ] APScheduler (będzie w F3)
- [ ] Deployment (będzie w F3)
- [ ] Testy 🙈 (dodawaj od początku błagam)

---

## Faza 1 — Storage + API (tydzień 3-4)

**Cel**: zamienić pickle na prawdziwy storage, dodać API.

- [ ] Qdrant: embeddingi ofert, deduplikacja po cosine similarity
- [ ] Postgres + SQLAlchemy: metadata ofert, historia analiz
- [ ] Redis: cache embeddingów (żeby nie licensować co chwilę)
- [ ] FastAPI: GET /offers, POST /run-analysis, GET /report/{id}
- [ ] Match Agent z scoringiem 1-10

---

## Faza 2 — Rozszerzona analiza (tydzień 5-6)

**Cel**: więcej źródeł, więcej agentów, observability.

- [ ] Trend Analysis Agent (batch tygodniowy: co zniknęło, pojawiło się, rośnie)
- [ ] Pracuj.pl scraper (rozszerzenie base_scraper)
- [ ] Langfuse: tracing na każdym nodzie grafu
- [ ] Conditional edge: human-in-loop przed wysłaniem raportu
- [ ] Testy jednostkowe agentów (pytest + fake LLM)

---

## Faza 3 — UI + Scheduling (tydzień 7-8)

**Cel**: ładny frontend, automatyczne uruchamianie, gotowe do pokazania.

- [ ] Next.js dashboard:
  - Lista ofert z filtrami
  - Widok skill gapów
  - Raport w formie strony (nie pliku MD)
  - Trigger "run analysis" z UI
- [ ] APScheduler: scrape codziennie o 8 rano, analiza w niedzielę
- [ ] docker-compose: Qdrant + Postgres + Redis + API + UI

---

## Faza 4 — Deployment + Polerowanie (po tydzień 8, jak będzie czas)

- [ ] Azure Container Apps / AWS ECS / GCP Cloud Run
- [ ] domena + HTTPS
- [ ] Auth (minimum: klucz API)
- [ ] CI/CD (GitHub Actions: lint + test + deploy)
- [ ] README z screenami i "how to run"

---

## Uwagi

- **Kolejność faz może się zmieniać** — jeśli na rozmowie o pracę zapytają
  o deployment, możesz przeskoczyć do F3/F4.
- **Testy** — dodawaj do kodu od razu, nie czekaj na fazę. `pytest` zajmuje
  2 minuty a ratuje dupę.
- **Dlaczego Next.js zamiast Streamlit** — bo pokazuje, że umiesz ogarnąć
  warstwę frontendu, a AI Engineer z frontendem to rzadki skill.
  Streamlit jest git do prototypów, ale Next.js robi lepsze wrażenie w portfolio.
- **Storage na starcie** — pickle/JSON jest celowy. Nie ucz się Qdrant + Postgres + Redis
  równocześnie z LangGraphem. Najpierw ogarnij core, potem dokładaj warstwy.
