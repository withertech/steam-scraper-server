# coding: utf-8

import jwt
from fastapi import APIRouter, status, HTTPException
from fastapi import Depends, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from passlib.hash import bcrypt

import steam_scraper_server.db.user as user

router = APIRouter()
SECRET = "d2f66a381e1b266636d7d598a901197c2489b2e9d3614e73"
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.post(
    "/auth/token",
    tags=["auth"]
)
async def get_token(data: OAuth2PasswordRequestForm = Depends()):
    user_obj = await authenticate_user(data.username, data.password)

    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )
    access_token = jwt.encode(
        payload={"username": user_obj.username},
        key=SECRET
    )
    user_obj.key = access_token
    await user_obj.save()
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/auth/login",
    tags=["auth"]
)
async def login(data: OAuth2PasswordRequestForm = Depends()):
    token = await get_token(data)
    resp = RedirectResponse(
        url="/user",
        status_code=status.HTTP_302_FOUND)
    resp.set_cookie("token", token["access_token"])
    return resp


@router.post(
    "/auth/register",
    tags=["auth"],
    response_model=user.User_Pydantic
)
async def register(data: OAuth2PasswordRequestForm = Depends()):
    user_obj = user.User(
        username=data.username,
        password_hash=bcrypt.hash(data.password),
        key=jwt.encode(
            payload={"username": data.username},
            key=SECRET
        ))
    await user_obj.save()
    resp = RedirectResponse(
        url="/login",
        status_code=status.HTTP_302_FOUND)
    return resp


@router.get(
    "/user",
    tags=["page"],
    response_class=HTMLResponse
)
async def user_page(token: str = Cookie("none")):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        user_ = await user.User.get(username=payload.get("username"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )
    resp = HTMLResponse(F"""
        <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="https://unpkg.com/twinklecss@1.1.0/twinkle.min.css"/>
</head>
<body>
    <div class="flex p-4 m-6 justify-center">
        <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4" method="POST" >
            <h1 class="block text-gray-700 text-lg font-bold mb-2" >{(await user.User_Pydantic.from_tortoise_orm(user_)).username}</h1> 
            <div class="flex items-center justify-between">
                <button onclick="window.location.href='/scraper/api/user/keys'" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                    Keys
                </button>
            </div>
            <br/>
            <div class="flex items-center justify-between">
                <button onclick="window.location.href='/scraper/api/user/delete'" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                    DELETE
                </button>
            </div>
            <br/>
            <div class="flex items-center justify-between">
                <button onclick="window.location.href='/scraper/api/'" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                    Home
                </button>
            </div>
        </div>
    </div>
</body>
</html>
        """)
    resp.set_cookie("token", token)
    return resp


@router.get(
    "/user/keys",
    tags=["page"],
    response_class=HTMLResponse
)
async def keys_page(token: str = Cookie("none")):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        user_ = await user.User.get(username=payload.get("username"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )
    resp = HTMLResponse(F"""
        <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="https://unpkg.com/twinklecss@1.1.0/twinkle.min.css"/>
</head>
<body>
    <div class="flex p-4 m-6 justify-center">
        <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
            <h1 class="block text-gray-700 text-lg font-bold mb-2" >API Key</h1>
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">
                    Key:
                </label>
                <label class="block text-gray-700 text-sm mb-2">
                    {(await user.User_Pydantic.from_tortoise_orm(user_)).key}
                </label>
            </div>
            <br/>
            <div class="flex items-center justify-between">
                <button onclick="window.location.href='/scraper/api/user'" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                    Back
                </button>
            </div>
        </div>
    </div>
</body>
</html>
        """)
    resp.set_cookie("token", token)
    return resp


@router.get(
    "/user/delete",
    tags=["page"],
    response_class=HTMLResponse
)
async def delete_page(token: str = Cookie("none")):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        user_ = await user.User.get(username=payload.get("username"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )
    resp = HTMLResponse(F"""
        <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="https://unpkg.com/twinklecss@1.1.0/twinkle.min.css"/>
</head>
<body>
    <div class="flex p-4 m-6 justify-center">
        <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2">
                    User {(await user.User_Pydantic.from_tortoise_orm(user_)).username} deleted
                </label>
            </div>
            <br/>
            <div class="flex items-center justify-between">
                <button onclick="window.location.href='/scraper/api/'" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                    Home
                </button>
            </div>
        </div>
    </div>
</body>
</html>
        """)
    await user_.delete()
    resp.set_cookie("token", token)
    return resp


async def authenticate_user(username: str, password: str):
    user_obj = await user.User.get(username=username)
    if not user_obj:
        return False
    if not user_obj.verify_password(password):
        return False
    return user_obj


@router.get(
    "/",
    tags=["page"],
    response_class=HTMLResponse
)
async def main_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="https://unpkg.com/twinklecss@1.1.0/twinkle.min.css"/>
</head>
<body>
    <div class="flex p-4 m-6 justify-center">
        <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4" method="POST" >
            <h1 class="block text-gray-700 text-lg font-bold mb-2" >Steamscraper API</h1>
            <div class="flex items-center justify-between">
                <button onclick="window.location.href='/scraper/api/login'" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                    Login
                </button>
            </div>
            <br/>
            <div class="flex items-center justify-between">
                <button onclick="window.location.href='/scraper/api/register'" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                    Register
                </button>
            </div>
            <br/>
            <div class="flex items-center justify-between">
                <button onclick="window.location.href='/scraper/api/docs'" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                    Docs
                </button>
            </div>
        </div>
    </div>
</body>
</html>
        """


@router.get(
    "/login",
    tags=["page"],
    response_class=HTMLResponse
)
async def login_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="https://unpkg.com/twinklecss@1.1.0/twinkle.min.css"/>
</head>
<body>
    <div class="flex p-4 m-6 justify-center">
        <form class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4" method="POST" action="/scraper/api/auth/login" >
            <h1 class="block text-gray-700 text-lg font-bold mb-2" >Login</h1>
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2" for="username">
                    Username
                </label>
                <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="username" name="username" type="text">
            </div>
            <div class="mb-6">
                <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
                    Password
                </label>
                <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline" id="password" name="password" type="password">
            </div>
            <div class="flex items-center justify-between">
                <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                    Sign In
                </button>
            </div>
        </form>
    </div>
</body>
</html>
        """


@router.get(
    "/register",
    tags=["page"],
    response_class=HTMLResponse
)
async def register_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register</title>
    <link rel="stylesheet" href="https://unpkg.com/twinklecss@1.1.0/twinkle.min.css"/>
</head>
<body>
    <div class="flex p-4 m-6 justify-center">
        <form class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4" method="POST" action="/scraper/api/auth/register" >
            <h1 class="block text-gray-700 text-lg font-bold mb-2" >Register</h1>
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2" for="username">
                    Username
                </label>
                <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="username" name="username" type="text">
            </div>
            <div class="mb-6">
                <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
                    Password
                </label>
                <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline" id="password" name="password" type="password">
            </div>
            <div class="flex items-center justify-between">
                <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                    Sign Up
                </button>
            </div>
        </form>
    </div>
</body>
</html>
        """
