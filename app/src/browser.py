from playwright.async_api import async_playwright

class BrowserManager:

    def __init__(self):
        self.browser = None
        self.page = None
        self.running = None

   
    async def start(self):
        if not self.running:
            # Start Playwright engine
            self.playwright = await async_playwright().start()
            
            # Launch Chromium using Edge channel
            self.browser = await self.playwright.chromium.launch(
                channel="msedge", 
                headless=True
            )
            
            # Create browser context
            self.context = await self.browser.new_context()
            
            # Open a new page
            self.page = await self.context.new_page()

            # IMAGE BLOCKING:
            # Intercept image requests and cancel them to improve performance
            await self.page.route("**/*.{png,jpg,jpeg,svg}", lambda route: route.abort())
            
            self.running = True
            print("Browser started with image blocking enabled for performance.")

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

