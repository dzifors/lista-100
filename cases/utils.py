from fastapi.templating import Jinja2Templates
from objects import settings

templates = Jinja2Templates(directory="templates")


def render_template(template, request, **params):
    return templates.TemplateResponse(
        template, {"request": request, "globals": settings, **params}
    )


def flash_login(request, message, type):
    return render_template("admin/login.html", request, flash=message, flash_type=type)
