
import logging, time
import os
from typing import Any
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("request_logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(filename='requests.log', mode='a', encoding="utf-8")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("{asctime} - {levelname}: {message}", style="{")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class RequestLoggingMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request,*args: Any, **kwds: Any) -> Any:

        response = self.get_response(request)
        user = request.user
        logger.info(msg=f"{datetime.now()} - User: {user} - Path: {request.path}")

        return response
    

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request,*args: Any, **kwargs: Any) -> Any:
        
        current_time = datetime.now().time()

        before = time(hour=18,minute=00) #type: ignore
        after = time(hour=21, minute=00) #type: ignore

        if current_time < before or current_time > after:
            # raise PermissionDenied
            return JsonResponse(
                {"message": "Sorry, chatroom API is closed."},
                status=403
            )
        return self.get_response(request)

class OffensiveLanguageMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response
        self.request_log = {} 

    def __call__(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        if request.method == 'POST':
            now = datetime.now()
            interval = timedelta(minutes=1)

            if ip not in self.request_log:
                self.request_log[ip] = []

            recent_requests = []
            for ts in self.request_log[ip]:
                if now - ts <= interval:
                    recent_requests.append(ts)
            self.request_log[ip] = recent_requests

            if len(recent_requests) >= 5:
                return JsonResponse(
                    {"message": "Only 5 messages per minute allowed."},
                    status=403
                )

            self.request_log[ip].append(now)

        return self.get_response(request)
    
class RolepermissionMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response
        self.protected_paths = [
            '/admin/',
            '/api/restricted/'
        ]

    def __call__(self, request, *args: Any, **kwds: Any) -> Any:
        path = request.path

        for protected in self.protected_paths:
            if path.startswith(protected):
                user = request.user
                # if not user.is_superuser and not user.is_staff:
                if not hasattr(user, 'role') or user.role not in ['admin', 'moderator']:
                    # raise PermissionDenied("Access Denied")
                    return JsonResponse(
                        {"message":"Not Allowed"}, status=403
                    )
                break
        return self.get_response(request)
    