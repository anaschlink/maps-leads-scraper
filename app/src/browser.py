from playwright.async_api import async_playwright

class BrowserManager:

    def __init__(self):
        self.browser = None
        self.page = None
        self.running = None

   
    async def start(self):
        if not self.running:
            # 1. Inicia o motor do Playwright
            self.playwright = await async_playwright().start()
            
            # 2. Lança o navegador Edge
            self.browser = await self.playwright.chromium.launch(
                channel="msedge", 
                headless=False
            )
            
            # 3. Cria um contexto (necessário para aplicar bloqueios e configurações)
            self.context = await self.browser.new_context()
            
            # 4. Cria a página dentro desse contexto
            self.page = await self.context.new_page()

            # 5. BLOQUEIO DE IMAGENS: Melhora muito a velocidade no Acer Nitro
            # Ele intercepta as requisições de imagem e as cancela
            await self.page.route("**/*.{png,jpg,jpeg,svg}", lambda route: route.abort())
            
            self.running = True
            print("Navegador iniciado com bloqueio de imagens para performance.")

        return self.browser, self.page

    async def get_page(self):
        if not self.running:
            raise Exception("Browser not iniciated")
        return self.page
        
    async def close(self):
        if self.running:
            if self.page:
                await self.page.close()

            if self.browser:
                await self.browser.close()
            
            if self.playwright:
                await self.playwright.stop()

            self.running = False

