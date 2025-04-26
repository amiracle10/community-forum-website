from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.timezone import now, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
import json
from .models import Post, Reply
from django.utils.timezone import now
from django.http import HttpResponse
from .forms import RegisterForm
from django.utils import timezone
from django.db.models import Q


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
    all_posts = Post.objects.all().order_by('-created_at')
    return render(request,'discussions.html',{
        'online_users': online_users,
        'recent_posts': recent_posts,
        'all_posts': all_posts
    
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
    online_users = get_online_users()
    recent_posts = Post.objects.order_by('-created_at')[:5]
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return HttpResponseForbidden()

    if request.method == 'POST':
        post.delete()
        return redirect('forum_category', category=post.category)



def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    online_users = get_online_users()
    recent_posts = Post.objects.order_by('-created_at')[:5]

    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        parent_reply = Reply.objects.filter(id=parent_id).first() if parent_id else None

        Reply.objects.create(
            user=request.user,
            post=post,
            content=content,
            parent=parent_reply
        )
        return redirect('post_detail', post_id=post.id)

    all_replies = Reply.objects.filter(post=post).select_related('user', 'parent').order_by('created_at')

    reply_map = {}
    top_level_replies = []

    for reply in all_replies:
        reply.temp_children = []
        reply_map[reply.id] = reply
        if reply.parent_id is None:
            top_level_replies.append(reply)

    for reply in all_replies:
        if reply.parent_id:
            parent = reply_map.get(reply.parent_id)
            if parent:
                parent.temp_children.append(reply)

    return render(request, 'post_detail.html', {
        'post': post,
        'replies': top_level_replies,
        'online_users': online_users,
        'recent_posts': recent_posts
    })


def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    if request.user != reply.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        post_id = reply.post.id
        reply.delete()
        return redirect('post_detail', post_id=post_id)
    
def search_posts(request):
    query = request.GET.get('q')
    if not query:
        return redirect('index')
    posts = Post.objects.filter(Q(title__icontains=query)).order_by('-created_at') if query else []

    online_users = get_online_users()
    recent_posts = Post.objects.order_by('-created_at')[:5]

    return render(request, 'search_results.html', {
        'query': query,
        'posts': posts,
        'online_users': online_users,
        'recent_posts': recent_posts,
    })