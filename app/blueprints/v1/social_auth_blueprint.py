from flask import Blueprint, Response, request
import bcrypt

from addons.builder import Builder
from addons.validate import (
  Schema,
  Multipart,
  Validation,
  DefaultPattern,
  Length,
  Required,
  Pattern
)

from datetime import datetime
from typing import Dict, Any
import secrets

from contants import Roles, Status

social_auth_bp = Blueprint("social_auth", __name__, url_prefix="/social-auth")

@social_auth_bp.route("/signup", methods=["POST"])
def signup():
    # TO-DO: handle file upload in a separate endpoint, using multiprocessing and job queue
    #  to avoid blocking the main thread and improve performance.
    avatar = request.files.get("avatar")

    # Avatar processing
    if not avatar:
        return Response({ "exception": {
            "message": "No file part",
            "code": "NO_FILE_PART",
            "details": { "field": "avatar" }
        } }, mimetype='application/json', status=400)
    if avatar.filename == '' or not avatar.filename:
        return Response({ "exception": {
            "message": "No selected file",
            "code": "NO_FILE_SELECTED",
            "details": { "field": "avatar" }
        } }, mimetype='application/json', status=400)
    if excep := Multipart.allowed_file(avatar.filename, allowed_ext={'png', 'jpg', 'jpeg', 'gif'}):
        return Response({ "exception": {
            "message": excep,
            "code": "INVALID_FILE_TYPE",
            "details": { "allowed_types": ['png', 'jpg', 'jpeg', 'gif'] }
        } }, mimetype='application/json', status=400)
    if excep := Multipart.too_large(avatar.content_length):
        return Response({ "exception": {
            "message": excep,
            "code": "FILE_TOO_LARGE",
            "details": { "max_size": 2 * 1024 * 1024 }
        } }, mimetype='application/json', status=400)
    data = request.form

    body: Dict[str, Any] = {
        "nickname": data.get("nickname"),
        "username": data.get("username"),
        "email": data.get("email"),
        "password": data.get("password"),
        "color": data.get("color"),
    }
    
    schema = [
        Validation(
            field="nickname",
            type=str,
            rules=(Length(min=3, max=30), Required()),
        ),
        Validation(
            field="username",
            type=str,
            rules=(Length(min=3, max=30),
                   Pattern(regex=DefaultPattern.USERNAME.value, flags=0),
                   Required()),
        ),
        Validation(
            field="email",
            type=str,
            rules=(Length(min=5, max=100),
                   Pattern(regex=DefaultPattern.EMAIL.value, flags=0),
                   Required()),
        ),
        Validation(
            field="password",
            type=str,
            rules=(Length(min=6, max=100), Required()),
        ),
        Validation(
            field="color",
            type=str,
            rules=(Required(),
                   Pattern(regex=DefaultPattern.HEX_COLOR.value, flags=0)),
        )
    ]

    if excep := Schema.validate(body, schema):
        return Response({ "exception": {
            "message": excep,
            "code": "VALIDATION_ERROR",
            "details": { "fields": schema }
        } }, mimetype='application/json', status=400)

    salt = bcrypt.gensalt()
    password_hashed = bcrypt.hashpw(body["password"], salt)
    
    # basic info
    user_id = Builder.query("users").fields(
        ["nickname", "username", "email", "password", "avatar", "color"]
    ).values(
        (
            body["nickname"],
            body["username"],
            body["email"],
            password_hashed,
            body["avatar"],
            body["color"],
        )
    ).create()
    
    # tokenization
    token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(64)
    expires_in = 3600  # 1 hour from now

    Builder.query("tokens").fields(
        ["user_id", "token", "refresh_token", "expires_in"]
    ).values(
        (
            user_id,
            token,
            refresh_token,
            expires_in
        )
    ).create()

    # user role
    (Builder.query("user_roles")
    .fields(["user_id", "role_id"])
    .values((user_id, Roles.DEFAULT.value,))
    .create())
    
    # user status
    (Builder.query("user_status")
    .fields(["user_id", "status"])
    .values((user_id, Status.OFFLINE.value,))
    .create())
    
    response_body: Dict[str, Any] = {
        "user_id": user_id,
        "token": token,
        "refresh_token": refresh_token,
        "expires_in": expires_in
    }

    return Response(response_body, mimetype='application/json', status=201)


@social_auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    body: Dict[str, Any] = {
        "identifier": data.get("identifier"),  # username or email
        "password": data.get("password"),
    }
    
    schema = [
        Validation(
            field="identifier",
            type=str,
            rules=(Length(min=3, max=100), Required()),
        ),
        Validation(
            field="password",
            type=str,
            rules=(Length(min=6, max=100), Required()),
        ),
    ]

    if excep := Schema.validate(body, schema):
        return Response({ "exception": {
            "message": excep,
            "code": "VALIDATION_ERROR",
            "details": { "fields": schema }
        } }, mimetype='application/json', status=400)

    user = (Builder.query("users")
        .fields(["id", "password_hash"])
        .where(f"username = '{body['identifier']}' OR email = '{body['identifier']}'")
        .read()
        .limit(1)
        .fetchone()
    )

    if not user or not bcrypt.checkpw(body["password"], user["password_hash"]):
        return Response({ "exception": {
            "message": "Invalid credentials",
            "code": "AUTH_ERROR",
            "details": { }
        } }, mimetype='application/json', status=401)

    # tokenization
    token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(64)
    expires_at = datetime.now().timestamp() + 3600  # 1 hour from now

    Builder.query("tokens").fields(
        ["user_id", "token", "refresh_token", "expires_at"]
    ).values(
        (
            user["id"],
            token,
            refresh_token,
            expires_at
        )
    ).create()

    response_body: Dict[str, Any] = {
        "user_id": user["id"],
        "token": token,
        "refresh_token": refresh_token,
        "expires_at": expires_at
    }

    return Response(response_body, mimetype='application/json', status=200)

@social_auth_bp.route("/logout", methods=["POST"])
def logout():
    data = request.get_json()
    user_id: int = data.get("user_id")
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1] if auth_header else None
    
    if not user_id or not token:
        return Response({ "exception": {
            "message": "User ID and token are required",
            "code": "LOGOUT_ERROR",
            "details": { "fields": ["user_id", "token"] }
        } }, mimetype='application/json', status=400)
    
    # check if token exists and belongs to the user
    existing_token = (Builder.query("tokens")
        .fields(["id"])
        .where(f"user_id = {user_id} AND token = '{token}'")
        .limit(1)
        .read()
        .fetchone()
    )
    
    if not existing_token:
        return Response({ "exception": {
            "message": "Invalid user ID or token",
            "code": "LOGOUT_ERROR",
            "details": { }
        } }, mimetype='application/json', status=400)
    
    deleted_rows = (Builder.query("tokens")
        .where(f"user_id = {user_id} AND token = '{token}'")
        .delete()
    )
    
    if deleted_rows == 0:
        return Response({ "exception": {
            "message": "Invalid user ID or token",
            "code": "LOGOUT_ERROR",
            "details": { }
        } }, mimetype='application/json', status=400)

    return Response(mimetype='application/json', status=203)

@social_auth_bp.route("/refresh-token", methods=["POST"])
def refresh_token():
    data = request.get_json()
    body: Dict[str, Any] = {
        "user_id": data.get("user_id"),
        "refresh_token": data.get("refresh_token"),
    }
    
    schema = [
        Validation(
            field="user_id",
            type=int,
            rules=(Required(),),
        ),
        Validation(
            field="refresh_token",
            type=str,
            rules=(Length(min=43, max=128), Required()),
        ),
    ]

    if excep := Schema.validate(body, schema):
        return Response({ "exception": {
            "message": excep,
            "code": "VALIDATION_ERROR",
            "details": { "fields": schema }
        } }, mimetype='application/json', status=400)

    existing_token = (Builder.query("tokens")
        .fields(["id"])
        .where(f"user_id = {body['user_id']} AND refresh_token = '{body['refresh_token']}'")
        .limit(1)
        .read()
        .fetchone()
    )

    if not existing_token:
        return Response({ "exception": {
            "message": "Invalid user ID or refresh token",
            "code": "TOKEN_REFRESH_ERROR",
            "details": { }
        } }, mimetype='application/json', status=400)

    # generate new tokens
    new_token = secrets.token_urlsafe(32)
    new_refresh_token = secrets.token_urlsafe(64)
    expires_at = datetime.now().timestamp() + 3600  # 1 hour from now

    updated_rows = (Builder.query("tokens")
        .fields(
            ["token", "refresh_token", "expires_at"]
        ).values(
            (
                new_token,
                new_refresh_token,
                expires_at
            )
        ).where(f"id = {existing_token['id']}")
        .update()
    )

    if updated_rows == 0:
        return Response({ "exception": {
            "message": "Failed to refresh token",
            "code": "TOKEN_REFRESH_ERROR",
            "details": { }
        } }, mimetype='application/json', status=500)

    response_body: Dict[str, Any] = {
        "user_id": body["user_id"],
        "token": new_token,
        "refresh_token": new_refresh_token,
        "expires_at": expires_at
    }

    return Response(response_body, mimetype='application/json', status=200)