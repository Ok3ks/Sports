import jwt
from django.conf import settings
from django.http import JsonResponse

PUBLIC_PATHS = ["/api/token/"]


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in PUBLIC_PATHS:
            return self.get_response(request)

        token = request.headers.get("X-API-Key")
        if not token:
            return JsonResponse({"error": "Missing X-API-Key header"}, status=401)

        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token has expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)

        return self.get_response(request)
