from django.urls import path
from polls import views

urlpatterns = [
    path('index/', views.index, name="index"),
    path('detail/<int:poll_id>', views.detail, name="poll_detail"),
    path('create/', views.create, name="poll_create"),
    path('detail/<int:poll_id>/answer/create', views.createAnswer, name="create_answer"),
    path('detail/<int:poll_id>/create-comment', views.createComment, name="create_comment"),
    path('login/', views.mylogin, name='login'),
    path('logout/', views.mylogout, name='logout')
]