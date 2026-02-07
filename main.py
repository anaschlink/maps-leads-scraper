import asyncio
from app.src.browser import BrowserManager
from app.src.navigator import MapsNavigator
from app.src.scraper import Scrapper
from app.data.exporter import ExportService

async def main():
    
    manager = BrowserManager()

    browser, page = await manager.start()

    navigator = MapsNavigator(page)
    scrapper = Scrapper(page)
    results = []

    try:
        await navigator.open_maps()
        await navigator.search("Padaria em São Caetano do Sul")

       
        cards = await scrapper.get_cards()
        print(f"Foram encontrados {len(cards)} cards.")

        
        for card in cards:
            try:
                await scrapper.open_card(card)
                
            
                raw_data = await scrapper.extract_all()

                results.append(raw_data)
                
                print(f"Extraído com sucesso: {raw_data['name']}")
            except Exception as e:
                print(f"Erro ao processar card: {e}")
                continue

        if results:
            ExportService.to_excel(results, "padarias_results.xlsx")
            print("Arquivo exportado com sucesso!")

    finally:

        await manager.close()

if __name__ == "__main__":

    asyncio.run(main())