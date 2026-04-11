import asyncio

import asgiref
import asgiref.sync

from celery import Celery
from src.auth.schemas import SendMailConfig
from src.auth.utils import build_html_email
from src.config import settings
from src.mail import create_message_schema, fm

celery_app = Celery(
    "celery",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)


@celery_app.task()
def send_mail(data: SendMailConfig):
    html_content = build_html_email(data["body"])
    message = create_message_schema(
        recipients=data["recipients"],
        subject=data["subject"],
        body=html_content,
    )
    # asyncio.run(fm.send_message(message))
    asgiref.sync.async_to_sync(fm.send_message)(message)
