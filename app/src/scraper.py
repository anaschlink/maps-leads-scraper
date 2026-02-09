import re
from playwright.async_api import Page


class Scrapper:
    def __init__(self, page: Page):
        self.page = page
        self.card_selector = "a.hfpxzc"
        self.feed_selector = 'div[role="feed"]'

    async def get_cards(self):
        return await self.page.query_selector_all(self.card_selector)

    async def scroll_feed_and_collect_cards(
        self,
        limit: int = 50,
        max_scrolls: int = 20,
        pause_ms: int = 800,
    ):
        await self.page.wait_for_selector(self.feed_selector, timeout=30000)
        feed = self.page.locator(self.feed_selector)

        previous_count = 0
        stable_rounds = 0

        for i in range(max_scrolls):
            cards = await self.get_cards()
            print(f"Scroll {i + 1}/{max_scrolls}: {len(cards)} load cards")

            if len(cards) >= limit:
                return cards[:limit]

            if len(cards) == previous_count:
                stable_rounds += 1
            else:
                stable_rounds = 0
                previous_count = len(cards)

            if stable_rounds >= 3:
                print("No new feed results")
                break

            await feed.evaluate("(el) => { el.scrollTop = el.scrollHeight; }")
            await self.page.wait_for_timeout(pause_ms)

        return await self.get_cards()

    async def open_card(self, card):
        await card.click()
        await self.page.wait_for_selector('[data-item-id="address"]')

    async def extract_all(self):
        return {
            "name": await self.extract_name(),
            "rating": await self.extract_rating(),
            "address": await self.extract_address(),
            "phone": await self.extract_phone(),
            "website": await self.extract_website(),
        }

    # fallbacks usados no main.py quando price vierem vazios

    async def extract_price_from_card(self, card):
        return await self._extract_price_from_card_locator(card)

    # extratores 

    async def extract_name(self) -> str | None:
        el = self.page.locator("h1.DUwDvf").first
        return await self._first_text(el)

    async def extract_rating(self) -> str | None:
        el = self.page.locator('div.F7nice span[aria-hidden="true"]')
        return await self._first_text(el)

    async def extract_price(self) -> str | None:
        # 1) Painel de detalhes: "R$ ... por pessoa"

        el = self.page.locator('div.BfvpR:has-text("por pessoa")').first
        if not await el.count():
            el = self.page.locator('div:has-text("por pessoa")').first
        if await el.count():
            return (await el.inner_text()).split("\n")[0].strip()

        # 2) fallback: procurar qualquer "R$" no card/painel

        return await self._extract_price_from_card_locator(self.page)

    async def extract_address(self) -> str | None:
        el = self.page.locator('[data-item-id="address"]').first
        return await self._first_text(el)

    async def extract_phone(self) -> str | None:
        el = self.page.locator('button[data-item-id^="phone:tel"]')
        return await self._first_text(el)

    async def extract_website(self) -> str | None:
        el = self.page.locator('[data-item-id="authority"]').first
        return await self._first_text(el)



    async def _first_text(self, locator):
        if await locator.count() == 0:
            return None
        return (await locator.inner_text()).strip()


    async def _extract_price_from_card_locator(self, root):
        # Card list: "R$ 40–60" perto do rating
        el = root.locator('div.AJB7ye span:has-text("R$")').first
        if await el.count():
            return (await el.inner_text()).strip()

        # fallback: qualquer "R$"
        el = root.locator('span:has-text("R$")').first
        if await el.count():
            return (await el.inner_text()).strip()

        return None
