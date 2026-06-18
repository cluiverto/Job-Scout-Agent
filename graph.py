from typing import TypedDict

from langgraph.graph import StateGraph

from agents.report import generate_report
from agents.skill_gap import SkillGapReport, run_analysis
from scrapers.justjoin_scraper import scrape_offers
from storage import save_offers
from storage.qdrant import filter_new_offers, init_collection


class GraphState(TypedDict):
    category: str
    max_pages: int
    report: SkillGapReport | None
    report_path: str


def scrape_node(state: GraphState) -> dict:
    offers = scrape_offers(
        category=state["category"],
        max_pages=state["max_pages"],
        valid_categories={"ai", "ml", "data"},
    )
    save_offers(offers)
    print(f"  ✓ Pobrano {len(offers)} ofert")
    return {}


def dedup_node(state: GraphState) -> dict:
    from storage import load_offers

    init_collection()
    offers = load_offers()
    new_offers = filter_new_offers(offers)
    if new_offers:
        print(f"  ✓ {len(new_offers)} nowych ofert po dedup")
    return {}


def skill_gap_node(state: GraphState) -> dict:
    report = run_analysis()
    return {"report": report}


def report_node(state: GraphState) -> dict:
    report = state["report"]
    if report is None:
        raise RuntimeError("Brak raportu skill_gap — pominięto analizę?")
    md = generate_report(report)
    path = state["report_path"]
    import pathlib

    pathlib.Path(path).write_text(md, encoding="utf-8")
    print(f"  ✓ Raport zapisano → {path}")
    return {}


builder = StateGraph(GraphState)

builder.add_node("scrape", scrape_node)
builder.add_node("dedup", dedup_node)
builder.add_node("skill_gap", skill_gap_node)
builder.add_node("report", report_node)

builder.set_entry_point("scrape")
builder.add_edge("scrape", "dedup")
builder.add_edge("dedup", "skill_gap")
builder.add_edge("skill_gap", "report")
builder.set_finish_point("report")

graph = builder.compile()
