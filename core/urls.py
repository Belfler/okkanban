from django.urls import path
from django.contrib.auth.views import LogoutView

from core.views import *

app_name = 'core'

urlpatterns = [
    path('', Summary.as_view(), name='summary'),
    path('register/', Registration.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('projects/create/', ProjectCreation.as_view(), name='project_creation'),
    path('projects/<int:project_pk>/', ProjectDetail.as_view(), name='project_detail'),
    path('projects/<int:project_pk>/leave/', ProjectLeave.as_view(), name='project_leave'),
    path('projects/<int:project_pk>/settings/', ProjectSettings.as_view(), name='project_settings'),
    path('projects/<int:project_pk>/delete/', ProjectDeletion.as_view(), name='project_deletion'),
    path('projects/<int:project_pk>/columns/create/', ColumnCreation.as_view(), name='column_creation'),
    path('projects/<int:project_pk>/columns/<int:column_pk>/change/', ColumnChange.as_view(), name='column_change'),
    path('projects/<int:project_pk>/columns/<int:column_pk>/delete/', ColumnDeletion.as_view(), name='column_deletion'),
    path('projects/<int:project_pk>/tasks/create/', TaskCreation.as_view(), name='task_creation'),
    path('projects/<int:project_pk>/tasks/<int:task_pk>/change/', TaskChange.as_view(), name='task_change'),
    path('projects/<int:project_pk>/tasks/<int:task_pk>/delete/', TaskDeletion.as_view(), name='task_deletion'),
    path('projects/<int:project_pk>/invite/', Invitation.as_view(), name='invite_person'),
    path('projects/<int:project_pk>/join/<uuid:uuid>/', JoiningProject.as_view(), name='join_project'),
]
