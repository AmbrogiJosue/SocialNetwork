
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API
    path("posts/<str:feed>/", views.get_posts, name="posts"),
    path("post", views.post, name="post"),
    path("profile/<str:user>", views.profile, name="profile"),
    path("follow/<str:user>", views.follow, name="follow"),
    path("like/<int:post_id>", views.like, name="like"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("recomendations", views.recomendations, name="recomendations"),
    path("comment/<int:post_id>", views.comment, name="comment"),
    path("updateProfile", views.update_profile, name="updateProfile"),
    path("deletePost/<int:post_id>", views.delete_post, name="deletePost"),
    path("deleteUser/<str:user>", views.delete_user, name="deleteUser"),
]
