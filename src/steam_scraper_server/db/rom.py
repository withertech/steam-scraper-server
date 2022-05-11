from tortoise.contrib.pydantic import pydantic_model_creator

from steam_scraper_server.models.images_result import ImagesResult
from tortoise import fields
from tortoise.models import Model


class Rom(Model):
    md5 = fields.CharField(32, unique=True, pk=True)
    system = fields.TextField()


class Media(Model):
    md5 = fields.CharField(32, unique=True, pk=True)
    head = fields.TextField()
    tall = fields.TextField()
    hero = fields.TextField()
    logo = fields.TextField()
    icon = fields.TextField()


Rom_Pydantic = pydantic_model_creator(Rom, name="Rom")
Media_Pydantic = pydantic_model_creator(Media, name="Media")
