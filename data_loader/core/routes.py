""""Routes приложения """
from core.components import Application
from labor_protect.views import labor_protect_route


def setup_routes(app: Application):
    """Настройка подключаемых route к приложению."""
    app.include_router(labor_protect_route)
