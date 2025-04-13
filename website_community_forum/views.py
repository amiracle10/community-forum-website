from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

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