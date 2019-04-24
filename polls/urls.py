from django.urls import path
from polls import views

urlpatterns = [
    path('index/', views.index, name="index"),
    path('detail/<int:poll_id>', views.detail, name="poll_detail"),
    path('create/', views.create, name="poll_create"),
    path('update/<int:poll_id>', views.update, name="poll_update"),
    path('delete/<int:question_id>', views.delete_question, name="delete_question"),
    path('<int:question_id>/add-choice/', views.add_choice, name="add_choice"),
    path('<int:question_id>/update-choice/', views.update_choice, name="update_choice"),
    path('detail/<int:poll_id>/answer/create', views.createAnswer, name="create_answer"),
    path('detail/<int:poll_id>/create-comment', views.createComment, name="create_comment"),
    path('login/', views.mylogin, name='login'),
    path('logout/', views.mylogout, name='logout'),
    path('change_password/', views.changePassword, name='change_password'),
    path('register/', views.register, name='register'),
    path('api/questions/<int:question_id>/choices/', views.get_choices_api, name="get_choices_api"),
    path('api/<int:question_id>/add-choice/', views.add_choice_api, name='add_choice_api'),
    path('api/<int:question_id>/update-choice/', views.update_choice_api, name='update_choice_api'),
    path('api/delete-choice/<int:choice_id>', views.delete_choice_api, name='delete_choice_api'),
]