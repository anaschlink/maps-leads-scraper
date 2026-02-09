import asyncio
import argparse
from tqdm import tqdm

from app.src.browser import BrowserManager
from app.src.navigator import MapsNavigator
from app.src.scraper import Scrapper
from app.data.exporter import ExportService
from app.data.processor import DataProcessor


async def main(query: str, output: str):
    manager = BrowserManager()
    browser, page = await manager.start()

    navigator = MapsNavigator(page)
    scrapper = Scrapper(page)
    processor = DataProcessor()

    results = []
    seen_hrefs = set()
    seen_keys = set()

    try:
        await navigator.open_maps()
        await navigator.search(query)

        cards = await scrapper.scroll_feed_and_collect_cards(
            limit=50,
            max_scrolls=25,
            pause_ms=800
        )

        print(f"Cards found: {len(cards)}")

        for card in tqdm(cards, desc="Processing cards", unit="card"):
            try:
                href = await card.get_attribute("href")
                if href and href in seen_hrefs:
                    continue
                if href:
                    seen_hrefs.add(href)

                await scrapper.open_card(card)
                raw_data = await scrapper.extract_all()

                # Ensure minimum usable data before processing
                processor.validate_required_fields(raw_data)

                clean = {
                    "name": processor.normalize_text(raw_data.get("name")),
                    "rating": processor.normalize_rating(raw_data.get("rating")),
                    "address": processor.normalize_address(raw_data.get("address")),
                    "phone": processor.normalize_phone(raw_data.get("phone")),
                    "website": processor.normalize_text(raw_data.get("website")),
                }

                # Deduplicate based on normalized identity
                key = (
                    (clean.get("name") or "").lower(),
                    (clean.get("address") or "").lower(),
                )
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                results.append(clean)
                print(f"Extracted: {clean.get('name')}")

            except Exception as e:
                print(f"Extraction error: {e}")
                continue

        if results:
            filename = output if output.lower().endswith(".xlsx") else f"{output}.xlsx"
            ExportService.to_excel(results, filename)
            print(f"Export completed -> {filename}")
        else:
            print("No results collected")

    finally:
        await manager.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--output", required=True, help="Output filename")
    args = parser.parse_args()

    asyncio.run(main(args.query, args.output))
