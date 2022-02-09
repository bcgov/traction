import os
import time

import uvicorn
from fastapi import FastAPI

# from api.db.errors import DoesNotExist, AlreadyExists
from api.endpoints.routes.webhooks import get_webhookapp
from api.core.config import settings
from api.endorser_main import get_endorserapp

os.environ["TZ"] = settings.TIMEZONE
time.tzset()


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        debug=settings.DEBUG,
        middleware=None,
    )
    return application


app = get_application()
webhook_app = get_webhookapp()
app.mount("/webhook", webhook_app)

endorser_app = get_endorserapp()
app.mount("/endorser", endorser_app)


# @app.exception_handler(DoesNotExist)
# async def does_not_exist_exception_handler(request: Request, exc: DoesNotExist):
#     return JSONResponse(
#         status_code=status.HTTP_404_NOT_FOUND,
#         content={"message": str(exc)},
#     )


# @app.exception_handler(AlreadyExists)
# async def already_exists_exception_handler(request: Request, exc: AlreadyExists):
#     return JSONResponse(
#         status_code=status.HTTP_409_CONFLICT,
#         content={"message": str(exc)},
#     )


@app.get("/", tags=["liveness"])
def main():
    return {"status": "ok", "health": "ok"}


if __name__ == "__main__":
    print("main.")
    uvicorn.run(app, host="0.0.0.0", port=8080)
