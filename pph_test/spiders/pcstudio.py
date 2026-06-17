"""
pcstudio test spider for Zyte Scrapy Cloud.

PURPOSE: a single, cheap experiment — does Scrapy Cloud's (datacenter) IP get
past pcstudio.in's Cloudflare and return real products? If the job finishes with
a healthy item count and NO "Just a moment" challenge in the log, the free unit
is usable for this store and we can expand. If items = 0 and the log shows a
Cloudflare challenge, the datacenter IP is blocked and we keep the Raspberry Pi.

It just yields items (Scrapy Cloud stores + counts them automatically) — no
database writes, so it's safe to run and easy to read the result.
"""
import scrapy


class PcstudioSpider(scrapy.Spider):
    name = "pcstudio"
    allowed_domains = ["pcstudio.in"]

    CATEGORIES = [
        "processor", "motherboard", "graphics-card",
        "ram", "ssd", "cabinet", "smps", "monitor",
    ]
    MAX_PAGES = 2  # pages per category — keep the test small

    def start_requests(self):
        # warm the homepage first (Cloudflare is friendlier once it's seen one hit)
        yield scrapy.Request(
            "https://www.pcstudio.in/",
            callback=self.after_warmup,
            dont_filter=True,
        )

    def after_warmup(self, response):
        self._check_block(response)
        for cat in self.CATEGORIES:
            yield scrapy.Request(
                f"https://www.pcstudio.in/product-category/{cat}/",
                callback=self.parse_listing,
                meta={"cat": cat, "page": 1},
            )

    def parse_listing(self, response):
        cat = response.meta["cat"]
        page = response.meta["page"]

        if self._check_block(response):
            return

        products = response.css("li.product")
        count = 0
        for p in products:
            title = (
                p.css(".woocommerce-loop-product__title::text").get()
                or p.css("h2::text").get()
                or p.css("h3::text").get()
            )
            url = (
                p.css("a.woocommerce-LoopProduct-link::attr(href)").get()
                or p.css("a::attr(href)").get()
            )
            price = (
                p.css(".price ins .amount::text").get()
                or p.css(".price .amount::text").get()
                or p.css(".price bdi::text").get()
            )
            img = (
                p.css("img::attr(data-src)").get()
                or p.css("img::attr(data-lazy-src)").get()
                or p.css("img::attr(src)").get()
            )
            if not title or not price:
                continue
            count += 1
            yield {
                "site": "pcstudio",
                "category": cat,
                "title": title.strip(),
                "price": price.strip(),
                "url": url,
                "image": img,
            }

        self.logger.info(
            "RESULT %s page %s -> %s products (HTTP %s)",
            cat, page, count, response.status,
        )

        if count and page < self.MAX_PAGES:
            nxt = page + 1
            yield scrapy.Request(
                f"https://www.pcstudio.in/product-category/{cat}/page/{nxt}/",
                callback=self.parse_listing,
                meta={"cat": cat, "page": nxt},
            )

    def _check_block(self, response):
        """Log loudly if Cloudflare served a challenge instead of the page."""
        body = response.text[:3000].lower()
        if "just a moment" in body or "checking your browser" in body or "cf-chl" in body:
            self.logger.warning("BLOCKED: Cloudflare challenge on %s", response.url)
            return True
        return False
