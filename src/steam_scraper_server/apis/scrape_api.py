# coding: utf-8
from __future__ import annotations

from typing import Dict, List  # noqa: F401

import fastapi
import requests
from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    Path,
    Query,
    Response,
    Security,
    status,
)
from pydantic.networks import HttpUrl

from steam_scraper_server.models.error_result import ErrorResult
from steam_scraper_server.models.extra_models import TokenModel  # noqa: F401
from steam_scraper_server.models.images_result import ImagesResult
from steam_scraper_server.models.images_result_images import ImagesResultImages

router = APIRouter()


@router.get(
    "/scrape",
    responses={
        200: {"model": ImagesResult, "description": "Urls to the images for the rom"},
        0: {"model": ErrorResult, "description": "unexpected error"},
    },
    tags=["scrape"],
    summary="Scrapes a rom for steam rom manager from screenscraper.fr using name of file and md5 sum",
)
async def scrape(
        filename: str = Query(None, description="name of the rom"),
        md5: str = Query(None, description="md5 of the rom"),
) -> ImagesResult | ErrorResult:
    # res = ErrorResult(code=0, message=filename)
    res = ImagesResult(name=filename, system=md5, images=ImagesResultImages(
        head="https://example.com/",
        tall="https://example.com/",
        hero="https://example.com/",
        logo="https://example.com/",
        icon="https://example.com/"
    ))

    return res
