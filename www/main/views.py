from django.http import HttpResponse
from django.shortcuts import render_to_response


def front(req):
    return HttpResponse('Here I am!')
