from playwright.async_api import Page, TimeoutError as PWTimeout

class MapsNavigator():

    def __init__(self, page: Page):
        self.page = page
        self.search_selectors = [
            'input[name="q"]',
            'input[role="combobox"][name="q"]',
            'form input[name="q"]',
            'input[aria-label="Pesquise no Google Maps"]',
            'input[aria-label="Pesquisar no Google Maps"]',
            'input[aria-label="Search Google Maps"]',
        ]
        self.feed_selector = 'div[role="feed"]'

    
    
    async def open_maps(self):
        print("Opening Google Maps...")
        try:
            
            await self.page.goto(
                "https://www.google.com/maps", 
                wait_until="domcontentloaded", 
                timeout=60000 
            )

            await self.page.wait_for_load_state("networkidle", timeout=60000)
            
            await self._try_accept_consent()

           
            sel = await self._find_search_input(timeout_each=8000)
            print(f"Google Maps loaded. Search input OK: {sel}")
            
        except Exception as e:
            print(f"Error opening Google Maps: {e}")
            await self.page.screenshot(path="error_opening_maps.png", full_page=True)
             # Save HTML as well for debugging.
            html = await self.page.content()
            with open("error_opening_maps.html", "w", encoding="utf-8") as f:
                f.write(html)
            raise

    async def search(self, query: str):
        print(f"Starting search for: {query}")

        # Ensure there is no consent overlay blocking interactions.
        await self._try_accept_consent()

        # Find the search input and interact with it using focus.
        sel = await self._find_search_input(timeout_each=8000)
        print(f"Search input found: {sel}")

        box = self.page.locator(sel).first
        await box.click()
        await box.fill(query)
        await self.page.keyboard.press("Enter")

        # Wait for results: sometimes the feed shows up, sometimes it takes longer.
        try:
            await self.page.wait_for_selector(self.feed_selector, timeout=30000)
        except PWTimeout:

            # Fallback: sometimes the feed is not present, but cards/links or the main pane is 

            await self.page.wait_for_selector('a.hfpxzc, div[role="main"]', timeout=30000)

        print("Resultados carregados.")

    async def _find_search_input(self, timeout_each: int = 8000) -> str:
        last_err = None
        for sel in self.search_selectors:
            try:
                await self.page.wait_for_selector(sel, state="visible", timeout=timeout_each)
                return sel
            except Exception as e:
                last_err = e
                continue
        # If not found, dump assets so you can inspect what actually loaded.
        await self.page.screenshot(path="maps_debug.png", full_page=True)
        html = await self.page.content()
        with open("maps_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        raise RuntimeError(f"Could not find the search input. Last error: {last_err}")

    async def _try_accept_consent(self):
        # Common consent buttons in PT-BR/EN.
        candidates = [
            'button:has-text("Aceitar tudo")',
            'button:has-text("Aceitar")',
            'button:has-text("Concordo")',
            'button:has-text("I agree")',
            'button:has-text("Accept all")',
        ]
        for sel in candidates:
            try:
                btn = self.page.locator(sel).first
                if await btn.is_visible(timeout=1200):
                    await btn.click()
                    await self.page.wait_for_timeout(400)
                    print("Consent accepted.")
                    return
            except Exception:
                pass
