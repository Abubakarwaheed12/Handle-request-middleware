from enum import Enum
from django.conf import settings 
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.shortcuts import HttpResponse

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)
CACHE_TTL = 60 

def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
        print('HTTP_X_FORWARDED_FOR', ip)
    else:
        ip = request.META.get('REMOTE_ADDR')
        print('REMOTE_ADDR', ip)
    return ip


class NumRequests(Enum):
    gold = 10
    silver = 7 
    bronze = 2 


class RequestHandlerMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response 
        print("MiddleWare Initilize")


    def __call__(self, request):
        if cache.get(get_ip(request)) is None:
            print("ip is none ")
            num_of_req = 1
            if request.user.is_authenticated:
                groups = request.user.groups.all()
                if groups.exists():
                    for group in groups:
                        req = NumRequests[group.name.upper()].value
                        if num_of_req < req:
                            num_of_req = req

            cache.set(get_ip(request), num_of_req, CACHE_TTL)
        else:
            data = int(cache.get(get_ip(request)))
            if data <= 0:
                return HttpResponse("You Are Blocked please try again. You will be unblocked after one minute automatically........!!!!! ")
            cache.set(get_ip(request), data - 1, CACHE_TTL)
        response = self.get_response(request)
        return response 