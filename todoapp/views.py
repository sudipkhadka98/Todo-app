from typing import Any
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, viewsets, status
from .serializers import TodoSerializer
from django.db.models import Q
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from .models import Todo, APIKey
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import NewUserForm
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework import permissions
from rest_framework.response import Response

# signup, login, and logout views
class SignupTodo(CreateView):
    form_class = NewUserForm
    template_name = 'user/signup.html'
    success_url = '/login/'

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, "Sign-up successful. You can now log in.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid sign-up information.")
        return super().form_invalid(form)

class LoginTodo(LoginView):
    template_name = 'user/login.html'
    next_page = '/'

class LogoutTodo(LogoutView):
    next_page = '/login/' 

# CRUD todo views
class ListTodo(LoginRequiredMixin, ListView):
    login_url = '/login/'
    model = Todo
    template_name = 'todo/listtodo.html'
    context_object_name = 'todo_data'
 

    def get_queryset(self):
        current_user = self.request.user
        if not current_user.is_authenticated:
            return Todo.objects.none()
        
        queryset = Todo.objects.filter(user=current_user)

        # Get search parameters from GET request
        q = self.request.GET.get('q')
        completed = self.request.GET.get('completed')
        importance = self.request.GET.get('importance')
        min_duration = self.request.GET.get('min_duration')
        max_duration = self.request.GET.get('max_duration')

        # Apply filters based on search parameters
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))
        if completed in ['true', 'false']:
            queryset = queryset.filter(completed=(completed == 'true'))
        if importance and importance in dict(Todo.IMPORTANCE_CHOICES).keys():
            queryset = queryset.filter(importance=importance)
        if min_duration:
            queryset = queryset.filter(duration__gte=min_duration)
        if max_duration:
            queryset = queryset.filter(duration__lte=max_duration)

        return queryset

class DetailTodo(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    model = Todo
    fields = ["title", "description", "completed", "duration", "importance"]
    template_name = 'todo/detailtodo.html'
    context_object_name = 'todo'
    pk_url_kwarg = 'todo_id'

class CreateTodo(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    model = Todo
    fields = ["title", "description", "completed", "duration", "importance"]
    template_name = 'todo/create.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class UpdateTodo(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    model = Todo
    fields = ["title", "description", "completed", "duration", "importance"]
    template_name = 'todo/updatetodo.html'
    pk_url_kwarg = 'todo_id'
    success_url = '/'

class DeleteTodo(LoginRequiredMixin, DeleteView):
    login_url = '/login/'
    model = Todo
    template_name = 'todo/deletetodo.html'
    pk_url_kwarg = 'todo_id'
    success_url = '/'

#rest api
class IsAuthenticatedOrValidAPIKey(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return True
        
        api_key = request.META.get('HTTP_AUTHORIZATION')
        if api_key:
            try:
                key_obj = APIKey.objects.get(key=api_key)
                if key_obj:
                    return True
            except APIKey.DoesNotExist:
                return False
        return False
    

class CustomTodoAPI(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrValidAPIKey]
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

    def get_queryset(self):
        api_key = self.request.META.get('HTTP_AUTHORIZATION')
        if api_key:
            try:
                key_obj = APIKey.objects.get(key=api_key)
                user = key_obj.user
                return self.queryset.filter(user=user)
            except APIKey.DoesNotExist:
                return Todo.objects.none()  # Return an empty queryset if the API key is invalid

        user = self.request.user
        if user and user.is_authenticated:
            return self.queryset.filter(user=user)

        return Todo.objects.none()  # Return an empty queryset if the user is not authenticated

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        if instance.user != request.user:
            return Response({'detail': 'Not authorized to update this todo item.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.user != request.user:
            return Response({'detail': 'Not authorized to delete this todo item.'}, status=status.HTTP_403_FORBIDDEN)
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

