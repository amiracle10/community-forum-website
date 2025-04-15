from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.timezone import now, timedelta


# Create your views here.
def index(request):
    online_users = get_online_users()
    return render(request, 'index.html', {'online_users': online_users})

def forum_category(request, category):
    return render(request, 'forum_category.html', {'category': category})


def discussion_board(request):

    return render(request,'discussions.html' )

def about_board(request):

    return render(request, 'about.html')

def topics_board(request):

    return render(request, 'topics.html')

def events_board(request):

    return render(request, 'events.html')


#function to login
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(60 * 60 * 24 * 30)

            return redirect('index')
        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password',
                'remember_checked': bool(remember_me)
            })

    return render(request, 'login.html', {
        'remember_checked': False
    })


#function to logout
def user_logout(request):
    logout(request)
    return redirect('index')

#fucntionto get active user to the side menu
def get_online_users():
    users = User.objects.all()
    active_users = []

    for user in users:
        last_seen = cache.get(f'seen_{user.id}')
        if last_seen and now() - last_seen < timedelta(minutes=5):
            active_users.append(user)

    return active_users