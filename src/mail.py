from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import SecretStr

from src.config import settings

BASEDIR = Path(__file__).resolve().parent
fm = FastMail(
    ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=SecretStr(settings.MAIL_PASSWORD),
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_HOST,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.USE_CREDENTIALS,
        VALIDATE_CERTS=settings.VALIDATE_CERTS,
        MAIL_FROM=settings.MAIL_FROM_ADDRESS,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        TEMPLATE_FOLDER=BASEDIR / "templates",
        # MAIL_DEBUG= ,
        # SUPPRESS_SEND= ,
        # TIMEOUT= ,
        # LOCAL_HOSTNAME= ,
        # CERT_BUNDLE= ,
    )
)


def create_message_schema(
    *,
    recipients: list[str],
    subject: str = "",
    body: str = "",
    subtype: MessageType = MessageType.html,
):
    schema = MessageSchema(
        recipients=recipients,  # type: ignore
        subject=subject,
        subtype=subtype,
        body=body,
    )
    return schema
