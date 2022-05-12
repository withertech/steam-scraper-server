import json
import os.path

root_path = ""
AUTH_SECRET = "000000000000000000000000000000000000000000000000"
SCRAPE_SECRET = "000000000000000000000000000000000000000000000000"
if os.path.exists("/opt/scraper/conf/scraper.json"):
    with open("/opt/scraper/conf/scraper.json", "r") as file:
        data = json.load(file)
        root_path = data.get("prefix", "")
        AUTH_SECRET = data.get("auth_secret", "000000000000000000000000000000000000000000000000")
        SCRAPE_SECRET = data.get("scrape_secret", "000000000000000000000000000000000000000000000000")
