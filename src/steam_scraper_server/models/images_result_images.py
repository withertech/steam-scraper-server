# coding: utf-8

from __future__ import annotations

import re  # noqa: F401
from datetime import date, datetime  # noqa: F401
from typing import Any, Dict, List, Optional  # noqa: F401

from pydantic import AnyUrl, BaseModel, EmailStr, validator  # noqa: F401


class ImagesResultImages(BaseModel):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.

    ImagesResultImages - a model defined in OpenAPI

        head: The head of this ImagesResultImages.
        tall: The tall of this ImagesResultImages.
        hero: The hero of this ImagesResultImages.
        logo: The logo of this ImagesResultImages.
        icon: The icon of this ImagesResultImages.
    """

    head: AnyUrl
    tall: AnyUrl
    hero: AnyUrl
    logo: AnyUrl
    icon: AnyUrl


ImagesResultImages.update_forward_refs()
