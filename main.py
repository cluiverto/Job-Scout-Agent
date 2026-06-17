import sys

from graph import graph


def main(category: str = "ai", max_pages: int = 3):
    state = {
        "category": category,
        "max_pages": max_pages,
        "report_path": "raport.md",
    }
    print("Job Scout Agent — uruchamianie pipeline'u...")
    for step, output in enumerate(graph.stream(state), 1):
        print(f"\nKrok {step}: {list(output.keys())[0]}")
    print("\n✅ Gotowe! Otwórz raport.md")


if __name__ == "__main__":
    args = sys.argv[1:]
    kwargs = {}
    if args:
        kwargs["category"] = args[0]
    if len(args) > 1:
        kwargs["max_pages"] = int(args[1])
    main(**kwargs)
