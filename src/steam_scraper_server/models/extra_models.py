# coding: utf-8

from pydantic import BaseModel


class TokenModel(BaseModel):
    """Defines a token model."""

    sub: str


class RegisterModel(BaseModel):
    username: str
    password: str


RegisterModel.update_forward_refs()
