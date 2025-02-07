from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.core.files.storage import default_storage

from .models import User, Post, Comment
from .forms import EditProfile


def index(request):

     # Authenticated users view their inbox
    if request.user.is_authenticated:
        return render(request, "network/index.html")

    # Everyone else is prompted to sign in
    else:
        return HttpResponseRedirect(reverse("login"))

# Get all the users that the current user does not follow to display them in the recomendation section
def recomendations(request):
    if request.user.is_authenticated:
        user = User.objects.get(username = request.user.username)
        recomendations = User.objects.exclude(followers = user)
        recomendations = recomendations.exclude(username = user.username)
        recomendations = recomendations.exclude(username__in = user.followers.all())
        recomendations = recomendations[:10]
        return JsonResponse([recomendation.serialize() for recomendation in recomendations], safe=False)
    else:
        return HttpResponseRedirect(reverse("login"))

@csrf_exempt
def edit(request, post_id):
    # Access the function only if the user is the author of the post
    if request.user == Post.objects.get(pk = post_id).author:
        if request.method == "POST": 
            data  = json.loads(request.body)
            content = data.get("content", "")
            post = Post.objects.get(pk = post_id)
            post.content = content
            # Set edited to true to show the post as edited
            post.edited = True
            post.save()
        return  JsonResponse(post.serialize(), safe=False)
    else:
        return HttpResponseRedirect(reverse("login"))

@csrf_exempt
def comment(request, post_id):
    if request.user.is_authenticated:
        # Handle the request to create a new comment or to get all the comments of a post depending on the request method
        if request.method == "POST": 
            data  = json.loads(request.body)
            content = data.get("content", "")
            post = Post.objects.get(pk = post_id)
            comment = Comment(author = request.user, post=post,content = content)
            comment.save()
            return JsonResponse(comment.serialize(), safe=False,status=201)
        else:
            post = Post.objects.get(pk = post_id)
            comments = Comment.objects.filter(post = post)
            return JsonResponse([comment.serialize() for comment in comments], safe=False)
    else:
        return HttpResponseRedirect(reverse("login"))

def like(request, post_id):
    if request.user.is_authenticated:
        post_id = Post.objects.get(pk = post_id)
        # Toggle between liking and unliking the post
        if request.user in post_id.likes.all():
            post_id.likes.remove(request.user)
            return JsonResponse({"message": "Unliked"})
        else:
            post_id.likes.add(request.user)
            return JsonResponse({"message": "Liked"})
    else:
        return HttpResponseRedirect(reverse("login"))

def follow(request, user):
    if request.user.is_authenticated:
        user = User.objects.get(username = user)
        # Toggle between following and unfollowing the user
        if request.user in user.followers.all():
            user.followers.remove(request.user)
            return JsonResponse({"message": "Unfollowed"})
        else:
            user.followers.add(request.user)
            return JsonResponse({"message": "Followed"})
    else:
        return HttpResponseRedirect(reverse("login"))

def profile(request, user):
    if request.user.is_authenticated:
        # Get a user's information to display in the profile page  
        user = User.objects.get(username = user)
        return JsonResponse(user.serialize(), safe=False)
    else:
        return HttpResponseRedirect(reverse("login"))
    
def get_posts(request, feed):
    if request.user.is_authenticated:
        # Check for the type of feed to get the posts from
        if feed == 'all':
            posts = Post.objects.all()
        elif feed == 'following':
            following = User.objects.filter(followers = request.user)
            posts = Post.objects.filter(author__in = following)
        else: 
            # If the feed is a username, get the posts of that user
            user_feed = User.objects.get(username = feed) 
            posts = Post.objects.filter(author = user_feed)
        # Sort the posts by newest to oldest
        posts = posts.order_by("-date").all()
        # Set a django Paginator object to 10 posts per page
        paginator = Paginator(posts, 10)
        # Get the page number from the request
        page_number = request.GET.get('page')
        # Get the page object of that page number
        page_obj = paginator.get_page(page_number)
        #  Serialize all the posts in the page object and return them as a json response
        posts = [post.serialize() for post in page_obj]
        return JsonResponse({'posts': posts, 'has_next': page_obj.has_next()})
    else:
        return HttpResponseRedirect(reverse("login"))

@csrf_exempt
def post(request):
    # Check if the current user is authenticated
    if request.user.is_authenticated:
        if request.method == "POST":
            # If the user is authenticated and the request method is POST, then the request body contains the content of the post
            content = request.POST.get("content")
            # Get the content of the post and save it in the database
            image = request.FILES.get("image")
            post = Post (
                author = request.user,
                content = content,
            )
            if image is not None:
                file = default_storage.save(image.name, image)
                post.image = file
            post.save()
        return JsonResponse(post.serialize(), safe=False, status=201)
    else:
        return HttpResponseRedirect(reverse("login"))

def login_view(request):
    # Check if the request user is already logged in
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@csrf_exempt
def update_profile(request):
    profile = User.objects.get(username = request.user.username)
    if profile.is_authenticated:
        if request.method == "POST":
            name = request.POST.get("name", "")
            bio = request.POST.get("bio", "")
            link = request.POST.get("link", "")
            profile_pic = request.FILES.get("profilepic")
            header_pic = request.FILES.get("headerpic")
            if profile_pic is not None:
                profilepic = default_storage.save(profile_pic.name, profile_pic)
                profile.profile_pic.delete()
                profile.profile_pic = profilepic
            if header_pic is not None:
                headerpic = default_storage.save(header_pic.name, header_pic)
                profile.header_pic.delete()
                profile.header_pic = headerpic
            profile.name = name
            profile.bio = bio 
            profile.link = link
            profile.save()
            return JsonResponse(profile.serialize(), safe=False, status=201)
    else:
        return HttpResponseRedirect(reverse('login'))

def delete_post(request, post_id):
    if request.user.is_authenticated:
        post = Post.objects.get(pk = post_id)
        if request.user == post.author:
            post.delete()
            return JsonResponse({"message": "Post deleted"})
        else:
            return JsonResponse({"error": "You are not the author of this post"})
    else:
        return HttpResponseRedirect(reverse("login"))

def delete_user(request, user):
    if request.user.is_authenticated:
        user = User.objects.get(username = user)
        if request.user == user:
            user.delete()
            return JsonResponse({"message": "User deleted"})
        else:
            return JsonResponse({"error": "Forbidden"})
    else:
        return HttpResponseRedirect(reverse("login"))