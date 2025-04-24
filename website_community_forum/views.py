from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.timezone import now, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
import json
from .models import Post
from django.utils.timezone import now
from django.http import HttpResponse
from .forms import RegisterForm


# Create your views here.
def index(request):
    online_users = get_online_users()
    recent_posts = Post.objects.order_by('-created_at')[:5]
    return render(request, 'index.html', {
        'online_users': online_users,
        'recent_posts': recent_posts
    })


def forum_category(request, category):
    posts = Post.objects.filter(category=category).order_by('-created_at')
    online_users = get_online_users()
    recent_posts = Post.objects.order_by('-created_at')[:5]
    return render(request, 'forum_category.html', {
        'category': category,
        'posts': posts,
        'online_users': online_users,
        'recent_posts': recent_posts
    })


def discussion_board(request):
    online_users = get_online_users()
    recent_posts = Post.objects.order_by('-created_at')[:5]
    return render(request,'discussions.html',{
        'online_users': online_users,
        'recent_posts': recent_posts
    
    } )

def about_board(request):
    online_users = get_online_users()
    recent_posts = Post.objects.order_by('-created_at')[:5]

    return render(request, 'about.html'
                  ,{
        'online_users': online_users,
        'recent_posts': recent_posts
    
    })

def topics_board(request):
    online_users = get_online_users()
    recent_posts = Post.objects.order_by('-created_at')[:5]

    return render(request, 'topics.html' ,{
        'online_users': online_users,
        'recent_posts': recent_posts
    
    })

def events_board(request):
    online_users = get_online_users()
    recent_posts = Post.objects.order_by('-created_at')[:5]

    return render(request, 'events.html',{
        'online_users': online_users,
        'recent_posts': recent_posts
    
    })


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

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

                 
def user_logout(request):
    if request.user.is_authenticated:
        cache.delete(f'seen_{request.user.id}')
        logout(request)
    return redirect('index')

#fucntion to get active user to the side menu
def get_online_users():
    users = User.objects.all()
    active_users = [] #empty array(online users)

    for user in users:
        last_seen = cache.get(f'seen_{user.id}')
        if last_seen and now() - last_seen < timedelta(minutes=5):
            active_users.append(user)

    return active_users


#create post using modal(js)
@csrf_exempt
def create_post(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        data = json.loads(request.body)
        category = data.get('category')
        title = data.get('title')
        body = data.get('body')

        if not all([category, title, body]):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        post = Post.objects.create(
            category=category,
            title=title,
            body=body,
            author=request.user
        )

        return JsonResponse({'message': 'Post created', 'post_id': post.id}, status=201)

    return JsonResponse({'error': 'Invalid request'}, status=405)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    online_users = get_online_users()
    recent_posts = Post.objects.order_by('-created_at')[:5]

    return render(request, 'post_detail.html', {
        'post': post,
        'online_users': online_users,
        'recent_posts': recent_posts
    
    })

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return HttpResponseForbidden()

    if request.method == 'POST':
        post.delete()
        return redirect('forum_category', category=post.category)
    

def simulate_online_users(request):
    for user in User.objects.all():
        cache.set(f'seen_{user.id}', now())
    return HttpResponse("ready!.")
