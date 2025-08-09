#!/usr/bin/env -S uv run --script

# /// script
# requires-python = "==3.12.*"
# name = "PAYMENTS_APP"
# description = "PAYMENTS REST API TASK"
# author = "Vadim Sauschkin"
# author-email = "vadim.sauschkin@yandex.ru"
# license = "LICENSE.md"
# readme = "README.md"
# version = "0.1.0"
# entry-points = ["main = main:main"]
# dependencies = ["sqlalchemy[asyncio]", "sanic[ext]", "pydantic_settings", "pydantic", "psycopg2-binary", "pyjwt"]
# ///

import json as json_app
from contextvars import ContextVar
from functools import partial
from typing import Any, Coroutine, Optional

import jwt
from dotenv import load_dotenv
from sanic import Request, Sanic, file, json, text
from sanic.log import logger
from sanic.response import HTTPResponse
from sanic.worker.loader import AppLoader
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from config import config
from models import Account, Base, User
from routes import protected, setup_routes
from utils import hash_password


def create_database_engine() -> Engine:
    engine = create_engine(config.DATABASE_URL, echo=config.DEBUG, pool_recycle=3600)
    return engine


def attach_endpoints(app: Sanic) -> None:
    @app.get("/")
    def handler(request: Request) -> Coroutine[Any, Any, HTTPResponse]:
        return file(location="static/index.html", status=200)

    @app.get("/secret")
    @protected
    async def secret(request: Request) -> HTTPResponse:
        if not request.token:
            return text("To go fast, you must be fast.")
        else:
            ans = json_app.dumps(
                jwt.decode(
                    request.token, config.SECRET_KEY, algorithms=[config.ALGORITHM]
                )
            )
            ans_d = json_app.loads(ans)
            return json(ans_d)


def create_app(app_name: str) -> Sanic:
    app = Sanic(app_name, strict_slashes=False)
    engine: Engine = create_database_engine()
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    _base_model_session_ctx: ContextVar = ContextVar("session")

    async def inject_session(request: Request) -> None:
        request.ctx.session = Session()
        request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)

    app.register_middleware(inject_session, "request")

    async def close_session(request: Request, response: Any) -> None:
        if hasattr(request.ctx, "session_ctx_token"):
            _base_model_session_ctx.reset(request.ctx.session_ctx_token)
            request.ctx.session.close()

    app.register_middleware(close_session, "response")

    attach_endpoints(app)
    setup_routes(app)
    migrate_test_data(engine=engine)
    return app


def migrate_test_data(engine: Optional[Engine] = None) -> None:
    logger.info("Migrating started")
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Создание тестового администратора
        admin = User(
            email=config.TEST_ADMIN_EMAIL,
            password=hash_password(config.SECRET_KEY, config.TEST_ADMIN_PASSWORD),
            full_name="Test Admin",
            is_admin=True,
        )

        # Создание тестового пользователя
        user = User(
            email=config.TEST_USER_EMAIL,
            password=hash_password(config.SECRET_KEY, config.TEST_USER_PASSWORD),
            full_name="Test User",
        )

        # Создание счета для тестового пользователя
        account = Account(user=user, balance=100.0)

        session.add(user)
        session.add(admin)
        session.add(account)
        session.commit()

        logger.info("Test data migrated successfully")

    except Exception as e:
        session.rollback()
        logger.error(f"Error during test data migration: {str(e)}")
    finally:
        session.close()


if __name__ == "__main__":
    load_dotenv(".env")
    app_name = "PAYMENTS_APP"
    loader = AppLoader(factory=partial(create_app, app_name))
    app = loader.load()
    app.prepare(
        host=config.HOST,
        debug=config.DEBUG,
        workers=config.WORKERS,
        access_log=config.ACCESS_LOG,
        port=config.PORT,
        dev=config.DEV,
        auto_reload=config.AUTO_RELOAD,
    )
    Sanic.serve(primary=app, app_loader=loader)
