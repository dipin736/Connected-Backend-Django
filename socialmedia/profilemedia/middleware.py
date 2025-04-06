# middleware.py
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from jwt import decode as jwt_decode, InvalidTokenError
from django.contrib.auth import get_user_model

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope.get("query_string", b"").decode())
        token = query_string.get("token", [None])[0]

        if token:
            try:
                decoded = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = decoded.get("user_id")
                user = await get_user(user_id)
                scope["user"] = user
                print(f"[JWT MIDDLEWARE] ✅ Authenticated user: {user}")
            except InvalidTokenError as e:
                print(f"[JWT MIDDLEWARE] ❌ Invalid token: {e}")
                scope["user"] = AnonymousUser()
        else:
            print("[JWT MIDDLEWARE] ❌ No token provided")
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
