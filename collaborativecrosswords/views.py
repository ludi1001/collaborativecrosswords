import os

from django.shortcuts import render

def login(session):
    session['user'] = 'ella'

def is_logged_in(session):
    return 'user' in session and session['user'] == 'ella'

def index(request):
    if request.POST.get('password', '') == os.environ['CC_PASSWORD']:
        login(request.session)

    if is_logged_in(request.session):
        return render(request, 'index.html')
    else:
        return render(request, 'login.html')
