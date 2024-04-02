from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from starlette.responses import HTMLResponse, JSONResponse

from app.controllers import user_controller, post_controller
from app.services.user_service import UserService
from app.utils.dependencies import get_db
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Init app
    logger.info("App started..")
    yield
    # End the app
    logger.info("App exiting..")


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware,
                   allow_credentials=True,
                   allow_origins="*",
                   allow_methods="*",
                   allow_headers="*")
app.include_router(user_controller.user_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(post_controller.post_router, prefix="/api/v1/posts", tags=["Posts"])


@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!Doctype html>
    <html>
        <body>
            <h1>Posts Project</h1>
            <div class="btn-group">
                <a href="/docs"><button>SwaggerUI</button></a>
                <a href="/redoc"><button>Redoc</button></a>
            </div>
        </body>
    </html>
"""


@app.middleware("http")
async def authenticate(request: Request, call_next):
    """Authenticate requests middleware"""
    auth_header = request.headers.get("Authorization")
    permitted = _is_permitted(request.method, request.url.path, auth_header, request)

    if not permitted:
        return JSONResponse(content="Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED,
                            headers={"WWW-Authenticate": "Bearer"})

    return await call_next(request)


def _is_permitted(method: str, api, header: str, request: Request):
    """Is the user permitted to enter"""
    api_call = api[1:]
    if method == 'GET' and api_call in ['docs', 'openapi.json', 'favicon.ico']:
        return True

    excluded_apis = ['/register', '/token', '/']

    for ex_api in excluded_apis:
        if api_call.endswith(ex_api):
            return True

    scheme, data = (header or ' ').split(' ', 1)

    if scheme != 'Bearer':
        return False

    user_info = UserService(session=get_db()).authenticate(data)

    # set request object to use
    if user_info is not None:
        request.state.__setattr__('user', user_info)

    return user_info is not None


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=4500, reload=True)
