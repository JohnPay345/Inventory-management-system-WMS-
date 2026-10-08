from time import time

from fastapi import HTTPException, status
from joserfc import jwt
from joserfc.errors import BadSignatureError, ExpiredTokenError
from joserfc.jwk import OctKey

from shared.config import settings
from shared.schemas import TokenPayload

# 1. Инициализация ключа
ACCESS_TOKEN = str(settings.ACCESS_TOKEN)
REFRESH_TOKEN = str(settings.REFRESH_TOKEN)
ACCESS_TOKEN_LIFE = str(settings.ACCESS_TOKEN_LIFE)
REFRESH_TOKEN_LIFE = str(settings.REFRESH_TOKEN_LIFE)
access_key = OctKey.import_key(ACCESS_TOKEN)
refresh_key = OctKey.import_key(REFRESH_TOKEN)


# 2. Выпуск (Кодирование) токена
def generate_token(username: str, user_id: str, roles: list) -> dict:
  header = {"alg": "HS256"}
  access_payload = {
    "sub": user_id,
    "iat": int(time()),
    "exp": int(ACCESS_TOKEN_LIFE),
    "type": "AT",
    "username": username,
    "roles": roles,
  }
  refresh_payload = {
    "sub": user_id,
    "iat": int(time()),
    "exp": int(REFRESH_TOKEN_LIFE),
    "type": "RT",
    "username": username,
    "roles": roles,
  }

  access_token = jwt.encode(header, access_payload, access_key)
  refresh_token = jwt.encode(header, refresh_payload, refresh_key)
  return {"access_token": access_token, "refresh_token": refresh_token}


# 3. Проверка (Декодирование) токена
def verify_token(token_str: str, expected_type: str) -> TokenPayload:
  try:
    key_decode = access_key if expected_type == "AT" else refresh_key
    claims = jwt.decode(token_str, key_decode)
    payload = TokenPayload.model_validate(claims.claims)
    if payload.type != expected_type:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token type",
      )
    return payload
  except ExpiredTokenError:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail={
        "status": "fail",
        "error_code": "TOKEN_EXPIRED",
        "message": "Время действия сессии истекло. Пожалуйста, обновите токен",
      },
      headers={"WWW-Authenticate": "Bearer"},
    )
  except (BadSignatureError, Exception) as error:
    print(error)
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail={
        "status": "fail",
        "error_code": "INVALID_TOKEN",
        "message": "Предоставлен невалидный или измененный токен",
      },
    )
