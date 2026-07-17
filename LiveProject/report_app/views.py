import datetime

import jwt
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def token_view(request):
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "iat": now,
        "exp": now + datetime.timedelta(minutes=settings.JWT_EXPIRATION_MINUTES),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return JsonResponse({"token": token, "expires_in": settings.JWT_EXPIRATION_MINUTES * 60})
