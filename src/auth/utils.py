import html
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext

from src.auth.models import User
from src.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
url_token_ser = URLSafeTimedSerializer(
    settings.JWT_SECRET_KEY,
    settings.EMAIL_TOKEN_SALT,
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_token(
    user: User,
    extra: dict[str, Any] | None = None,
    refresh: bool = False,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(user.uid),
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "type": "refresh" if refresh else "access",
    }
    if extra:
        payload.update(extra)
    expire = now + (
        timedelta(days=settings.REFRESH_EXPIRE_DAYS)
        if refresh
        else timedelta(minutes=settings.ACCESS_EXPIRE_MINUTES)
    )
    payload["exp"] = expire
    token = jwt.encode(
        payload=payload,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )


def create_url_safe_token(data: dict[str, Any]) -> str:
    return url_token_ser.dumps(data)


def decode_urlsafe_token(token, max_age: int = 3600) -> Optional[dict[str, Any]]:
    try:
        return url_token_ser.loads(token, max_age=max_age)
    except Exception as e:
        print(str(e))
        return None


def build_html_email(body: str) -> str:
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>

<body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Arial,Helvetica,sans-serif;">

  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="padding:30px 0;">
    <tr>
      <td align="center">

        <!-- Main Container -->
        <table role="presentation" width="600" cellpadding="0" cellspacing="0"
               style="background-color:#ffffff;border-radius:8px;">

          <!-- Header -->
          <tr>
            <td style="background-color:#4f46e5;padding:20px;text-align:center;color:#ffffff;">
              <h1 style="margin:0;font-size:20px;font-weight:600;">
                Pagely
              </h1>
              <p style="margin:5px 0 0;font-size:13px;">
                Your book platform
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:30px;color:#333333;">

              <h2 style="margin:0 0 15px;font-size:18px;">
                Welcome 👋
              </h2>

              <p style="margin:0;font-size:15px;line-height:1.6;color:#555555;">
                {body}
              </p>

            </td>
          </tr>

          <!-- Divider (safe version instead of <hr>) -->
          <tr>
            <td style="padding:0 30px;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="border-top:1px solid #e5e7eb;"></td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Button -->
          <tr>
            <td align="center" style="padding:30px;">
              <table role="presentation" cellpadding="0" cellspacing="0">
                <tr>
                  <td bgcolor="#4f46e5" style="border-radius:5px;">
                    <a href="#"
                       style="display:inline-block;
                              padding:12px 20px;
                              font-size:14px;
                              color:#ffffff;
                              text-decoration:none;">
                      Get Started
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color:#f9fafb;padding:20px;text-align:center;font-size:12px;color:#999999;">
              <p style="margin:0;">
                © 2026 Pagely. All rights reserved.
              </p>
              <p style="margin:5px 0 0;">
                If you didn’t request this, you can ignore this email.
              </p>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>
"""
    return html_content
