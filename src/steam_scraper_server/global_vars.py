import json
import os.path

root_path = ""
if os.path.exists("/opt/scraper/conf/scraper.json"):
    with open("/opt/scraper/conf/scraper.json", "r") as file:
        data = json.load(file)
        root_path = data["prefix"]
