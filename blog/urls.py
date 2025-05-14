from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
    path('post/<slug:slug>/delete/', views.delete_post, name='delete_post'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('logout/', views.logout_view, name='logout'),
]