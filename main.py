import uvicorn

from app.api import app
from app.config import get_settings


def main():
    settings = get_settings()
    uvicorn.run(
        app,
        host=settings.api.host,
        port=settings.api.port,
        reload=True,
    )


if __name__ == "__main__":
    main()
