from collections.abc import AsyncGenerator
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from services.database import AsyncSessionLocal
from services.tokens import verify_token
from shared.enum import UserRole
from shared.schemas import TokenPayload
from shared.scheme.auth import auth_scheme


async def get_db() -> AsyncGenerator[AsyncSession]:
  async with AsyncSessionLocal() as session:
    yield session
    await session.commit()


def verify_access_token(
  credentials: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
) -> TokenPayload:
  token = credentials.credentials
  token_data = verify_token(token, "AT")
  return token_data


def verify_refresh_token(request: Request) -> TokenPayload:
  refresh_token = request.cookies.get("refresh_token")
  if not refresh_token:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail={
        "status": "fail",
        "error_code": "REFRESH_TOKEN_REQUIRED",
        "message": "Сессия истекла, необходим refresh токен",
      },
    )
  token_data = verify_token(refresh_token, "RT")
  return token_data


class PermissionChecker:
  def __init__(
    self,
    allowed_roles: list[UserRole],
    check_owner: bool = False,
  ):
    # allowed_roles: Список ролей, которым разрешен доступ к эндпоинту
    # check_owner: Нужно ли проверять, что user_id из токена совпадает с {user_id} из URL-пути
    self.allowed_roles = allowed_roles
    self.check_owner = check_owner

  async def __call__(
    self,
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
  ) -> TokenPayload:

    payload: TokenPayload = verify_token(token_str=credentials.credentials, expected_type="AT")

    # Если роли пользователя нет в списке разрешенных для этого эндпоинта
    if payload.roles not in self.allowed_roles:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
          "status": "fail",
          "error_code": "ROLE_NOT_ALLOWED",
          "message": f"Доступ запрещен для роли: {[role.value for role in payload.roles]}",
        },
      )

    # Если включен флаг check_owner и в URL есть параметр {user_id}
    if self.check_owner:
      path_user_id = request.path_params.get("user_id")

      if path_user_id is not None and str(payload.sub) != str(path_user_id):
        raise HTTPException(
          status_code=status.HTTP_403_FORBIDDEN,
          detail={
            "status": "fail",
            "error_code": "ACCESS_DENIED",
            "message": "Вы не можете просматривать или изменять чужие данные",
          },
        )
    return payload
