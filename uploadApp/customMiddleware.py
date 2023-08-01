from .jwt import aes, decode_jwt_token_and_return_validity
from django.conf import settings
from django.http import HttpResponse


class JWTHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        exclude_path = ['/', '/static', '/login/', '/downloadfile/28', '/media/', '/favicon.ico', '/media/biodata.xlsx']
        if request.path in exclude_path:
            return self.get_response(request)
        jwt_token = request.headers.get('Authorization', 'Bearer').replace('Bearer ', '')
        validity = decode_jwt_token_and_return_validity(settings.SECRET_KEY, jwt_token, settings.TOKEN_EXP)

        if validity["success"]:
            request.user_info = validity['payload']
            response = self.get_response(request)
        else:
            response = HttpResponse(status=validity["status_code"])

        return response
