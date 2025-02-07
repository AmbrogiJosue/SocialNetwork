from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    followers = models.ManyToManyField('self', blank=True, symmetrical=False, related_name="follow")
    profile_pic = models.ImageField(default='default.png', null=True, blank=True)
    header_pic = models.ImageField(default='defaultheader.png', null=True, blank=True)
    name = models.CharField(max_length=24, blank=True, null=True, default="")
    bio = models.CharField(max_length=128, blank=True, null=True, default="")
    link = models.URLField(max_length=64, blank=True, null=True, default="")

    def __str__(self):
        return f"{self.id} - User: {self.username}, {self.followers.count()} Followers"
    
    def serialize(self):
        return {
            "username": self.username,
            "name": self.name,
            "followers": [user.username for user in self.followers.all()],
            "following": [user.username for user in User.objects.filter(followers= self).all()],
            "date": self.date_joined.strftime("%b %Y"),
            "profile_pic": self.profile_pic.url,
            "header_pic": self.header_pic.url,
            "bio": self.bio,
            "link": self.link,
        }

class Post (models.Model): 
    author = models.ForeignKey("User",  on_delete=models.CASCADE, related_name="post_user")
    content = models.TextField(editable=True, max_length=264)
    date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField("User", related_name="post_likes", blank=True)
    edited = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True)

    def serialize(self):
        data = {
            "id": self.id,
            "author": self.author.username,
            "content": self.content,
            "date": self.date.strftime("%b %d %Y, %I:%M %p"),
            "likes": [user.username for user in self.likes.all()],
            "edited": self.edited,
            "image": None,
        }
        if self.image:
            data["image"] = self.image.url
        return data 

class Comment (models.Model):
    author = models.ForeignKey("User", on_delete=models.CASCADE, related_name="comment_user")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comment_post")
    content = models.TextField(editable=True, max_length=264)
    date = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "author": self.author.username,
            "content": self.content,
            "date": self.date.strftime("%b %d %Y, %I:%M %p"),
        }