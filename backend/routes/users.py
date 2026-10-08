from functools import partial
from time import time
from types import SimpleNamespace
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status as web_status
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.users import (
  repo_get_user_by_id,
  repo_user_create,
  repo_user_exists,
  repo_user_update,
)
from shared.dependency import get_db, verify_refresh_token
from shared.schemas import LoginRequest, RegisterRequest, ResponseSchema, TokenPayload
from use_cases.users import case_login, case_register, case_update_tokens


def user_repo(db: Annotated[AsyncSession, Depends(get_db)]):
  return SimpleNamespace(
    repo_user_exists=partial(repo_user_exists, db),
    repo_get_user_by_id=partial(repo_get_user_by_id, db),
    repo_user_create=partial(repo_user_create, db),
    repo_user_update=partial(repo_user_update, db),
  )


router = APIRouter()


@router.post("/login", response_model=ResponseSchema)
async def login(response: Response, login_data: LoginRequest, repo=Depends(user_repo)):
  tokens = await case_login(login_data, repo)
  response.set_cookie(
    key="refresh_token",
    value=tokens["refresh_token"],
    path="/api/refresh_token",
    max_age=int(time()) + 3600,
    samesite="lax",
    httponly=True,
  )
  return ResponseSchema.success(data=tokens["access_token"], message="Login is success")


@router.post("/register", response_model=ResponseSchema)
async def register(register_data: RegisterRequest, repo=Depends(user_repo)):
  new_user = await case_register(register_data, repo)
  return ResponseSchema.success(
    code=web_status.HTTP_201_CREATED, data=new_user, message="User is created"
  )


@router.post("/update_tokens", response_model=ResponseSchema)
async def update_tokens(
  response: Response,
  refresh_token_payload: Annotated[TokenPayload, Depends(verify_refresh_token)],
):
  new_tokens = await case_update_tokens(refresh_token_payload)
  response.set_cookie(
    key="refresh_token",
    value=new_tokens["refresh_token"],
    path="/api/refresh_token",
    max_age=int(time()) + 3600,
    samesite="lax",
    httponly=True,
  )
  return ResponseSchema.success(data=new_tokens["access_token"], message="Login is success")
