# coding: utf-8

from fastapi.testclient import TestClient

from steam_scraper_server.models.error_result import ErrorResult  # noqa: F401
from steam_scraper_server.models.images_result import ImagesResult  # noqa: F401


def test_scrape(client: TestClient):
    """Test case for scrape

    Scrapes a rom for steam rom manager from screenscraper.fr using name of file and md5 sum
    """
    params = [("filename", 'filename_example'), ("md5", 'md5_example')]
    headers = {
    }
    response = client.request(
        "GET",
        "/scrape",
        headers=headers,
        params=params,
    )

    # uncomment below to assert the status code of the HTTP response
    # assert response.status_code == 200
