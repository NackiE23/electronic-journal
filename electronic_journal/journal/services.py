from .models import *


def send_message(from_user: CustomUser, to_user: CustomUser, text: str) -> None:
    Message.objects.create(from_user=from_user, to_user=to_user, text=text)
