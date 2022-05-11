#!/usr/bin/env bash
uvicorn src.steam_scraper_server.main:app --host 127.0.0.1 --port 8080 --log-level trace