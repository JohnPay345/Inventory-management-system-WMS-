from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class SimpleBearerScheme(HTTPBearer):
  def __init__(self, auto_error: bool = True):
    # Отключаем авто-ошибку суперкласса, чтобы контролировать её вручную
    super().__init__(auto_error=False)

  async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
    # 1. Пытаемся извлечь из заголовка Bearer
    credentials: HTTPAuthorizationCredentials | None = await super().__call__(request)
    if credentials:
      return credentials

    # 2. Резервный вариант: ищем в Cookie
    access_token = request.cookies.get("access_token")
    if access_token:
      return HTTPAuthorizationCredentials(scheme="Bearer", credentials=access_token)

    # 3. Если токена нет вообще — отдаем кастомную ошибку
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail={
        "status": "fail",
        "error_code": "AUTH_REQUIRED",
        "message": "Для доступа к этому ресурсу необходима авторизация",
      },
    )


# Создаем экземпляр нашей схемы
auth_scheme = SimpleBearerScheme()
