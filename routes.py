from datetime import datetime, timedelta

from PIL import Image
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    status,
    UploadFile,
)
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
from cases.utils import flash_login, render_template, flash
from objects.articles import get_article, get_articles
from objects.lists import (
    get_edition,
    get_editions,
    get_list,
    get_edition_count,
    create_edition,
    SortingOptions,
    get_capitule,
    get_capitule_count,
    delete_edition,
)
from objects.users import User, logout, update_last_login
from state import visit_counter

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


@router.get("/aktualnosci/{article_id}")
async def article_page(request: Request, article_id: int):
    article = await get_article(article_id)

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    article = (article[0], article[1], markdown(article[2]), article[3])

    return render_template("article.html", request, article=article)


@router.get("/galeria")
async def gallery_page(request: Request):
    return render_template("gallery.html", request)


@router.get("/kapitula")
@router.get("/sklad")
async def capitule_page(request: Request):
    capitule = await get_capitule()

    return render_template("capitule.html", request, capitule=capitule)


@router.get("/listy")
async def lists_page(request: Request):
    editions = await get_editions(sort=SortingOptions.Descending)

    return render_template("lists.html", request, editions=editions)


@router.get("/listy/{edition_id}")
async def list_page(request: Request, edition_id: int):
    people = await get_list(edition_id)
    edition = await get_edition(edition_id)

    if not people or not edition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return render_template("list.html", request, people=people, edition=edition)


@router.get("/logotypy")
async def logotypes_page(request: Request):
    return render_template("logotypes.html", request)


# ADMIN ROUTES


@router.get("/admin")
async def admin_page(request: Request, current_user: User = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse("admin/login")

    edition_count = await get_edition_count()
    capitule_count = await get_capitule_count()

    return render_template(
        "admin/dashboard.html",
        request,
        page_visits=visit_counter.counter,
        edition_count=edition_count,
        capitule_count=capitule_count,
    )


@router.get("/admin/login")
async def login_page(request: Request, current_user: User = Depends(get_current_user)):
    if current_user:
        return RedirectResponse("/admin/dashboard")

    return render_template("/admin/login.html", request)


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

    response = RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
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


@router.get("/admin/editions/add")
async def editions_add(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return flash_login(request, "Nie jesteś zalogowany", "error")

    return render_template("admin/editions/add.html", request)


@router.get("/admin/editions")
async def editions_edit(
    request: Request, current_user: User = Depends(get_current_user)
):
    if not current_user:
        return flash_login(request, "Nie jesteś zalogowany", "error")

    editions = await get_editions()

    return render_template("admin/editions/dashboard.html", request, editions=editions)


@router.get("/admin/editions/{edition_id}")
async def edition_edit(
    request: Request, edition_id: int, current_user: User = Depends(get_current_user)
):
    if not current_user:
        return flash_login(request, "Nie jesteś zalogowany", "error")

    people = await get_list(edition_id)
    edition = await get_edition(edition_id)

    return render_template(
        "admin/editions/edit.html", request, people=people, edition=edition
    )


@router.get("/admin/editions/{edition_id}/members/add")
async def add_edition_member(
    request: Request, edition_id: int, current_user: User = Depends(get_current_user)
):
    if not current_user:
        return flash_login(request, "Nie jesteś zalogowany", "error")

    edition = await get_edition(edition_id)

    return render_template("admin/editions/members/add.html", request, edition=edition)


# API


@router.post("/api/editions/add")
async def post_editions_add(
    request: Request,
    thumbnail: UploadFile | None = None,
    edition_name: str = Form(),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return flash_login(request, "Nie jesteś zalogowany", "error")

    edition_id = await create_edition(edition_name)

    if thumbnail is not None:
        if thumbnail.file.read() != b"":
            thumbnail_image = Image.open(thumbnail.file)
            thumbnail_image.save(
                f"static/images/list-thumbnails/{edition_id}.png",
            )

    return flash("admin/editions/add.html", request, "Dodano pomyślnie", "success")


@router.get("/api/editions/delete/{edition_id}")
async def editions_delete(
    request: Request, edition_id: int, current_user: User = Depends(get_current_user)
):
    if not current_user:
        return flash_login(request, "Nie jesteś zalogowany", "error")

    await delete_edition(edition_id)

    editions = await get_editions()

    return flash(
        "admin/editions/edit.html",
        request,
        "Usunięto pomyślnie",
        "success",
        editions=editions,
    )


@router.post("/api/editions/{edition_id}/members")
async def editions_add_member(
    request: Request, edition_id: int, current_user: User = Depends(get_current_user)
):
    if not current_user:
        return flash_login(request, "Nie jesteś zalogowany", "error")

    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


# @router.post("/api/list/{edition_id}/tsv")
# async def post_list(
#     request: Request,
#     tsv_file: UploadFile,
#     edition_id: int,
#     current_user: User = Depends(get_current_user),
# ):
#     if not current_user:
#         return flash_login(request, "Nie jesteś zalogowany", "error")
#
#     tsv = await tsv_file.read()
#     reader = csv.reader(tsv.splitlines(), delimiter="\t")
#
#     lines = []
#
#     for line in reader:
#         lines.append(line)
#
#     # print(lines)
#     print(await fill_list(edition_id, lines))
#
#     return lines
