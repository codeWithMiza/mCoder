from django.urls import path, include
from .import views
from django.contrib import admin

urlpatterns = [
    path("", views.bloghome, name="blogHome"),
    path('search/', views.search, name="search"),
    path('postComment/', views.postComment, name="postComment"),
    path('<str:slug>/', views.blogPost, name="blogPost"),
    # path('postComment/', views.index, name="postComment"),
]