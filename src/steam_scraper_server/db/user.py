from fastapi import Depends
from passlib.handlers.bcrypt import bcrypt
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class User(Model):
    username = fields.CharField(50, pk=True, unique=True)
    key = fields.CharField(128)
    password_hash = fields.CharField(128)

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)


User_Pydantic = pydantic_model_creator(User, name="User")
