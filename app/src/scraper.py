from playwright.async_api import Page

class Scrapper:

    def __init__(self, page: Page ):
        self.page = page

    async def get_cards(self):
        return await self.page.query_selector_all('a.hfpxzc')

    async def open_card(self, card):
        await card.click()
        await self.page.wait_for_selector('[data-item-id="address"]')

    async def extract_name(self) -> str:
        title = await self.page.title()
        return title.replace(" - Google Maps", "")

    async def extract_rating(self):
        el = await self.page.query_selector('span[role="img"].ZkP5Je')
        if not el:
            return None
        text = await el.inner_text()
        return text.strip()
        
    
    async def extract_reviews_count(self):
        el = await self.page.query_selector('span[role="img"].ZkP5Je span.UY7F9')
        if not el:
            return None

        text = await el.inner_text() 
        return text.replace("(", "").replace(")", "")

    async def extract_price(self):
        el = await self.page.query_selector('span[role="img"][aria-label]')
        if not el:
            return None

        text = await el.inner_text()  
        return text.strip()

    async def extract_address(self):
        el = await self.page.query_selector('[data-item-id="address"]')
        return await el.inner_text() if el else None

    async def extract_phone(self):
        el = await self.page.query_selector('[data-item-id="phone"]')
        return await el.inner_text() if el else None

    async def extract_website(self):
        el = await self.page.query_selector('[data-item-id="authority"]')
        return await el.inner_text() if el else None
    
    async def extract_all(self):
        return {
            "name": await self.extract_name(),
            "rating": await self.extract_rating(),
            "reviews": await self.extract_reviews_count(),
            "price": await self.extract_price(),
            "address": await self.extract_address(),
            "phone": await self.extract_phone(),
            "website": await self.extract_website()
        }
