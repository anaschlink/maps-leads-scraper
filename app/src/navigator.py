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
        print("Abrindo o Google Maps...")
        try:
            # Usamos uma URL mais limpa e o wait_until mais rápido
            await self.page.goto(
                "https://www.google.com/maps", 
                wait_until="domcontentloaded", 
                timeout=60000  # Aumentamos para 60s por segurança
            )
            await self.page.wait_for_load_state("networkidle", timeout=60000)
            
            await self._try_accept_consent()

           
            sel = await self._find_search_input(timeout_each=8000)
            print(f"Google Maps carregado. Campo de busca OK: {sel}")
            
        except Exception as e:
            print(f"Erro ao abrir o Maps: {e}")
            await self.page.screenshot(path="error_opening_maps.png", full_page=True)
            # salva html também pra debug
            html = await self.page.content()
            with open("error_opening_maps.html", "w", encoding="utf-8") as f:
                f.write(html)
            raise

        #scroll

     
    async def search(self, query: str):
        print(f"Iniciando busca por: {query}")

        # garantir que não tem overlay travando
        await self._try_accept_consent()

        # achar o input e interagir com foco
        sel = await self._find_search_input(timeout_each=8000)
        print(f"Campo de busca encontrado: {sel}")

        box = self.page.locator(sel).first
        await box.click()
        await box.fill(query)
        await self.page.keyboard.press("Enter")

        # esperar resultados: às vezes aparece feed, às vezes demora mais
        try:
            await self.page.wait_for_selector(self.feed_selector, timeout=30000)
        except PWTimeout:
            # fallback: às vezes não é feed, mas aparece lista de cards/links
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
        # se não achou, faz dump pra você ver o que abriu
        await self.page.screenshot(path="maps_debug.png", full_page=True)
        html = await self.page.content()
        with open("maps_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        raise RuntimeError(f"Não encontrei o campo de busca. Último erro: {last_err}")

    async def _try_accept_consent(self):
        # botões comuns BR/EN
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
                    print("Consentimento aceito.")
                    return
            except Exception:
                pass
