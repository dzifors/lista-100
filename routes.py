from fastapi import APIRouter, HTTPException, Request, status
from fastapi.templating import Jinja2Templates

from markdown import markdown
from starlette.routing import NoMatchFound

from cases.utils import render_template
from objects.articles import get_article, get_articles


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
    article = (article[0], article[1], markdown(article[2]), article[3])

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Nie znaleziono wpisu"
        )

    return render_template("article.html", request, article=article)
