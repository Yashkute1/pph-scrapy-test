BOT_NAME = "pph_test"

SPIDER_MODULES = ["pph_test.spiders"]
NEWSPIDER_MODULE = "pph_test.spiders"

# Be a polite, browser-looking client. The whole point of this test is to see
# whether Scrapy Cloud's (datacenter) IPs get past pcstudio's Cloudflare, so we
# don't add any proxy here -- we want a clean read of the raw IP reputation.
ROBOTSTXT_OBEY = False
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

CONCURRENT_REQUESTS = 2
DOWNLOAD_DELAY = 2.0
DOWNLOAD_TIMEOUT = 30
RETRY_TIMES = 2

# Quieter logs, autothrottle so we don't hammer the site.
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2.0
AUTOTHROTTLE_MAX_DELAY = 10.0
LOG_LEVEL = "INFO"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
