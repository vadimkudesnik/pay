import json as json_app
from functools import wraps
from types import SimpleNamespace
from typing import Any, Coroutine, Dict, List, Optional

import jwt
from sanic import Blueprint, Request, Sanic, text
from sanic import Config as Config
from sanic.response import HTTPResponse, JSONResponse, json
from sqlalchemy.orm import Session

from config import config
from models import Account, Payment, User
from utils import hash_password, verify_signature

api = Blueprint("api", url_prefix="/api")


def check_token(request: Request) -> bool:
    if not request.token:
        return False

    try:
        jwt.decode(request.token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
    except jwt.exceptions.InvalidTokenError:
        return False
    else:
        return True


def protected(wrapped: Any) -> Coroutine[Any, Any, Any]:
    def decorator(f: Any) -> Any:
        @wraps(f)
        async def decorated_function(
            request: Request, *args: Any, **kwargs: Any
        ) -> Any:
            is_authenticated = check_token(request)

            if is_authenticated:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return text("You are unauthorized.", 401)

        return decorated_function

    return decorator(wrapped)


def is_admin(wrapped: Any) -> Coroutine[Any, Any, Any]:
    def decorator(f: Any) -> Any:
        @wraps(f)
        async def decorated_function(
            request: Request, *args: Any, **kwargs: Any
        ) -> Any:
            if not request.token:
                return text("Token error")
            else:
                ans = json_app.dumps(
                    jwt.decode(
                        request.token, config.SECRET_KEY, algorithms=[config.ALGORITHM]
                    )
                )
                ans_d = json_app.loads(ans)
                session: Session = request.ctx.session
                user: Optional[User] = (
                    session.query(User).filter_by(id=ans_d["user_id"]).first()
                )
                if not user:
                    return text("You are unauthorized.", 401)
                else:
                    if bool(user.is_admin):
                        response = await f(request, *args, **kwargs)
                        return response
                    else:
                        return text("You are unauthorized as admin.", 401)

        return decorated_function

    return decorator(wrapped)


@api.route("/auth", methods=["POST"])
async def auth(request: Request) -> JSONResponse:
    data: Dict[str, Any] = request.json
    email = data.get("email")
    password = hash_password(config.SECRET_KEY, str(data.get("password")))

    session: Session = request.ctx.session

    user: Optional[User] = session.query(User).filter_by(email=email).first()
    if not user or user.password != password:
        return json({"error": "Invalid credentials"}, status=401)

    token = jwt.encode(
        payload={"user_id": user.id},
        key=config.SECRET_KEY,
        algorithm=config.ALGORITHM,
    )

    return json(
        {
            "token": token,
        },
        status=200,
    )


@api.route("/users/me", methods=["GET"])
@protected
async def user_me(request: Request) -> HTTPResponse | JSONResponse:
    session: Session = request.ctx.session

    if not request.token:
        return text("Token error")
    else:
        ans = json_app.dumps(
            jwt.decode(request.token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        )
        ans_d = json_app.loads(ans)
        user: Optional[User] = (
            session.query(User).filter_by(id=ans_d["user_id"]).first()
        )
        if not user:
            return json({}, status=200)
        else:
            return json(
                {"user_id": user.id, "full_name": user.full_name, "email": user.email},
                status=200,
            )


@api.route("/users/me/accounts", methods=["GET"])
@protected
async def user_accounts(request: Request) -> HTTPResponse | JSONResponse:
    session: Session = request.ctx.session

    if not request.token:
        return text("Token error")
    else:
        ans = json_app.dumps(
            jwt.decode(request.token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        )
        ans_d = json_app.loads(ans)
        accounts: List[Account] = (
            session.query(Account).filter_by(user_id=ans_d["user_id"]).all()
        )
        if not accounts:
            return json({}, status=200)
        else:
            return json(
                [
                    {"id": acc.id, "account_id": acc.account_id, "balance": acc.balance}
                    for acc in accounts
                ],
                status=200,
            )


@api.route("/users/add", methods=["POST"])
@is_admin
async def create_user(request: Request) -> JSONResponse:
    data: Dict[str, Any] = request.json
    session: Session = request.ctx.session

    new_user = User(
        email=data["email"],
        password=hash_password(config.SECRET_KEY, data["password"]),
        full_name=data["full_name"],
        is_admin=data.get("is_admin", False),
    )
    try:
        session.add(new_user)
        session.commit()
    except Exception:
        return json({"error": "User exists"}, status=401)
    return json({"id": new_user.id}, status=201)


@api.route("/users/update", methods=["POST"])
@is_admin
async def update_user(request: Request) -> JSONResponse:
    data: Dict[str, Any] = request.json
    session: Session = request.ctx.session
    user: Optional[User] = session.query(User).filter_by(id=data["id"]).first()
    if not user:
        json({"error": "User doesnt exists"}, status=401)
    else:
        user.email = data.get("email", user.email)
        psw = str(data.get("password", ""))
        if psw != "":
            new_psw: Any = hash_password(config.SECRET_KEY, psw)
        user.password = new_psw
        user.full_name = data.get("full_name", user.full_name)
        user.is_admin = data.get("is_admin", False)

        try:
            session.commit()
        except Exception:
            return json({"error": "User exists"}, status=401)
    return json({"success": "success"}, status=201)


@api.route("/users/delete", methods=["POST"])
@is_admin
async def delete_user(request: Request) -> JSONResponse:
    data: Dict[str, Any] = request.json
    session: Session = request.ctx.session
    try:
        user: Optional[User] = session.query(User).filter_by(id=data["id"]).first()
        if not user:
            json({"error": "User doesnt exists"}, status=401)
        else:
            session.delete(user)
            session.commit()
    except Exception:
        return json({"error": "User doesnt exists"}, status=401)
    return json({"success": "user deleted"}, status=201)


@api.route("/users", methods=["GET"])
@is_admin
async def users_list(request: Request) -> JSONResponse:
    session: Session = request.ctx.session

    users: List[User] = session.query(User).all()
    return json(
        [
            {"id": user.id, "email": user.email, "full_name": user.full_name}
            for user in users
        ],
        status=201,
    )


@api.route("/users/<id:int>", methods=["GET"])
@is_admin
async def user_id(request: Request, id: int) -> JSONResponse:
    session: Session = request.ctx.session

    user: Optional[User] = session.query(User).filter_by(id=id).first()
    if not user:
        return json({}, status=200)
    else:
        return json(
            {"user_id": user.id, "full_name": user.full_name, "email": user.email},
            status=200,
        )


@api.route("/users/<id:int>/payments", methods=["GET"])
@is_admin
async def payments_id(request: Request, id: int) -> JSONResponse:
    session: Session = request.ctx.session

    payments: List[Payment] = session.query(Payment).filter_by(user_id=id).all()
    if not payments:
        return json({}, status=200)
    else:
        return json(
            [
                {
                    "transaction_id": payment.transaction_id,
                    "account_id": payment.account_id,
                    "payment": payment.amount,
                }
                for payment in payments
            ],
            status=200,
        )


@api.route("/users/<id:int>/accounts", methods=["GET"])
@is_admin
async def accounts_id(request: Request, id: int) -> JSONResponse:
    session: Session = request.ctx.session

    accounts: List[Account] = session.query(Account).filter_by(user_id=id).all()
    if not accounts:
        return json({}, status=200)
    else:
        return json(
            [
                {"id": acc.id, "account_id": acc.account_id, "balance": acc.balance}
                for acc in accounts
            ],
            status=200,
        )


@api.route("/users/me/payments", methods=["GET"])
@protected
async def user_payments(request: Request) -> HTTPResponse | JSONResponse:
    session: Session = request.ctx.session

    if not request.token:
        return text("Token error")
    else:
        ans = json_app.dumps(
            jwt.decode(request.token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        )
        ans_d = json_app.loads(ans)
        payments: List[Payment] = (
            session.query(Payment).filter_by(user_id=ans_d["user_id"]).all()
        )
        if not payments:
            return json({}, status=200)
        else:
            return json(
                [
                    {
                        "transaction_id": payment.transaction_id,
                        "account_id": payment.account_id,
                        "payment": payment.amount,
                    }
                    for payment in payments
                ],
                status=200,
            )


@api.route("/webhook", methods=["POST"])
async def process_webhook(request: Request) -> JSONResponse:
    data = request.json
    session: Session = request.ctx.session
    if not verify_signature(data, config.SECRET_KEY):
        return json({"error": "Invalid signature"}, status=400)
    try:
        user: Optional[User] = session.query(User).filter_by(id=data["user_id"]).first()
        if not user:
            return json({"error": "User not found"}, status=201)
        else:
            account: Optional[Account] = (
                session.query(Account)
                .filter_by(account_id=data["account_id"], user_id=data["user_id"])
                .first()
            )
            if not account:
                account = Account(
                    user_id=data["user_id"], account_id=data["account_id"], balance=0.0
                )
                session.add(account)
                session.commit()
            if (
                session.query(Payment)
                .filter_by(transaction_id=data["transaction_id"])
                .first()
            ):
                return json({"error": "Transaction already processed"}, status=400)
            payment = Payment(
                transaction_id=data["transaction_id"],
                user_id=data["user_id"],
                account_id=data["account_id"],
                amount=data["amount"],
            )

            account.balance += data["amount"]
            session.add(payment)
            session.commit()
            return json({"status": "success"}, status=201)
    except Exception as e:
        session.rollback()
        return json({"error": str(e)}, status=500)


@api.exception(Exception)  # Handle exceptions globally
async def handle_exception(request: Request, exception: Exception) -> JSONResponse:
    return json({"error": str(exception)}, status=500)


def setup_routes(app: Sanic[Config, SimpleNamespace]) -> None:
    app.blueprint(api)
