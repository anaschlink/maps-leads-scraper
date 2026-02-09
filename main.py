import asyncio
from app.src.browser import BrowserManager
from app.src.navigator import MapsNavigator
from app.src.scraper import Scrapper
from app.data.exporter import ExportService
import argparse

async def main(query: str, output: str):
    
    manager = BrowserManager()

    browser, page = await manager.start()

    navigator = MapsNavigator(page)
    scrapper = Scrapper(page)
    results = []
    seen_hrefs = set()
    seen_keys = set()


    try:
        await navigator.open_maps()
        await navigator.search(query)

       
        cards = await scrapper.scroll_feed_and_collect_cards(limit=50, max_scrolls=25, pause_ms=800)
        print(f"Foram encontrados {len(cards)} cards.")

        
        for card in cards:
            try:
                href = await card.get_attribute("href")
                if href:
                    if href in seen_hrefs:
                        continue
                    seen_hrefs.add(href)

                await scrapper.open_card(card)
                raw_data = await scrapper.extract_all()

                name = (raw_data.get("name") or "").strip().lower()
                address = (raw_data.get("address") or "").strip().lower()

                print("URL atual:", page.url)


                # chave final (mais robusta que só address)
                key = (name, address)
                if key in seen_keys:
                    continue
                # se address vier vazio, ainda dedup por nome
                if not address and name and (name, "") in seen_keys:
                    continue

                seen_keys.add(key)

                results.append(raw_data)
                print(f"Extraído com sucesso: {raw_data.get('name')}")

            except Exception as e:
                print(f"Erro ao processar card: {e}")
                continue

            if results:
                filename = output if output.lower().endswith(".xlsx") else f"{output}.xlsx"
                ExportService.to_excel(results, filename)
                print("Arquivo exportado com sucesso!")

    finally:

        await manager.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="the search value")
    parser.add_argument("--output", required=True, help="set the output file name")
    parsed= parser.parse_args()

    asyncio.run(main(parsed.query, parsed.output))