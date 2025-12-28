from fastapi import Request, HTTPException
import re

special_char_regex = re.compile(r'[@_!#$%^&*()<>?/\|}{~:]')
invalid_username_regex = re.compile(r'[^a-zA-Z0-9]')  


async def validateUserCreation(request: Request):
    body = await request.json()

    username = body.get("username")
    password = body.get("password")

    if not username or not validateUsername(username):
        raise HTTPException(status_code=422, detail="Invalid Username")

    if not password or not validatePassword(password):
        raise HTTPException(status_code=422, detail="Invalid Password")
    
    return True


def validateUsername(username: str) -> bool:
    if not username:
        return False

    if invalid_username_regex.search(username):
        return False

    return True


def validatePassword(password: str) -> bool:
    if not password or len(password) < 8:
        return False

    has_uppercase = any(ch.isupper() for ch in password)
    has_digit = any(ch.isdigit() for ch in password)
    has_special_char = special_char_regex.search(password) is not None
    has_whitespace = any(ch.isspace() for ch in password)

    if has_whitespace:
        return False

    if not has_uppercase:
        return False

    if not has_digit:
        return False

    if not has_special_char:
        return False

    return True


async def validateUserUpdate(request: Request):
    body = await request.json()

    username = body.get("username")
    password = body.get("password")

    if username is None and password is None:
        raise HTTPException(status_code=422, detail="No fields provided for update")

    if username is not None and not validateUsername(username):
        raise HTTPException(status_code=422, detail="Invalid Username")

    if password is not None and not validatePassword(password):
        raise HTTPException(status_code=422, detail="Invalid Password")
