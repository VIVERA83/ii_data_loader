"""The application launcher."""

import uvicorn
from core.settings import UvicornSettings

if __name__ == "__main__":
    settings = UvicornSettings()
    uvicorn.run(
        app="core.app:setup_app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        log_level=settings.log_level,
        reload=settings.reload,
    )
