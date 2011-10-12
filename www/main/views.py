from django.http import HttpResponse
from django.shortcuts import render_to_response


def front(req):
    return render_to_response('front.html', locals())
