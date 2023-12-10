from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from markdown import markdown

from cases.auth import (
    TOKEN_EXPIRE_TIME,
    authenticate_user,
    Token,
    create_access_token,
    get_current_user,
)
from cases.utils import flash_login, render_template
from objects.articles import get_article, get_articles
from objects.lists import get_edition, get_editions, get_list
from objects.users import User, logout, update_last_login


templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/")
@router.get("/home")
@router.get("/home/")
async def main_page(request: Request):
    return render_template("home.html", request)


@router.get("/aktualnosci")
async def news_page(request: Request):
    articles = await get_articles(10)
    articles = [
        (article[0], article[1], markdown(article[2]), article[3])
        for article in articles
    ]

    return render_template("news.html", request, articles=articles)


@router.get("/aktualnosci/{id}")
async def article_page(request: Request, id: int):
    article = await get_article(id)

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono wpisu"
        )

    article = (article[0], article[1], markdown(article[2]), article[3])

    return render_template("article.html", request, article=article)


@router.get("/listy")
async def lists_page(request: Request):
    editions = await get_editions()

    return render_template("lists.html", request, editions=editions)


@router.get("/listy/{id}")
async def list_page(request: Request, id: int):
    people = await get_list(id)
    edition = await get_edition(id)

    if not list or not edition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono listy"
        )

    return render_template("list.html", request, people=people, edition=edition)


#! ADMIN ROUTES


@router.get("/admin")
async def admin_page(request: Request, current_user: User = Depends(get_current_user)):
    if not current_user:
        return render_template("admin/login.html", request)

    return render_template("admin/dashboard.html", request)


@router.post("/admin/login", response_model=Token)
async def login_user(request: Request, email: str = Form(), password: str = Form()):
    if not email or not password:
        return flash_login(request, "Nie podano emaila lub hasła", "error")

    _user = await authenticate_user(email, password)

    if not _user:
        return flash_login(request, "Nieprawidłowy email lub hasło", "error")

    token_expires = timedelta(minutes=TOKEN_EXPIRE_TIME)

    token = create_access_token(
        data={"current_user": _user.email}, expires_delta=token_expires
    )

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="token", value=token)
    response.set_cookie(key="token_type", value="bearer")
    _user.last_login = datetime.now()
    await update_last_login(_user.email)

    return response


@router.get("/admin/logout")
async def logout_user(request: Request, current_user: User = Depends(get_current_user)):
    if not current_user:
        return flash_login(request, "Nie jesteś zalogowany", "error")

    return logout(request)
