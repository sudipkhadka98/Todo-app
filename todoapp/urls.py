from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('todoapp', views.CustomTodoAPI)
urlpatterns = [
    path('login/', views.LoginTodo.as_view(), name='login'),
    path('logout/', views.LogoutTodo.as_view(), name='logout'),
    path('signup/', views.SignupTodo.as_view(), name='signup'),

    path('', views.ListTodo.as_view(), name='index'),
    path('create/',views.CreateTodo.as_view(), name='createtodo'),
    path('detail-todo/<int:todo_id>', views.DetailTodo.as_view(), name='detailtodo'),
    path('update-todo/<int:todo_id>', views.UpdateTodo.as_view(), name='updatetodo'),
    path('delete-todo/<int:todo_id>', views.DeleteTodo.as_view(), name='deletetodo'),

    path('api/', include(router.urls))
]