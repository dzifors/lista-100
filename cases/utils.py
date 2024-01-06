from typing import Literal

from fastapi import Request
from fastapi.templating import Jinja2Templates

from objects import settings

templates = Jinja2Templates(directory="templates")

FlashType = Literal["error", "success"]


def render_template(template, request, **params):
    return templates.TemplateResponse(
        template, {"request": request, "globals": settings, **params}
    )


def flash(
    template: str, request: Request, message: str, flash_type: FlashType, **params
):
    return render_template(
        template, request, flash=message, flash_type=flash_type, **params
    )


def flash_login(request: Request, message: str, flash_type: FlashType, **params):
    return flash("admin/login.html", request, message, flash_type, **params)
