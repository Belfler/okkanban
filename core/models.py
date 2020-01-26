from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from core.managers import CustomUserManager


class CustomUser(AbstractUser):
    """
    Custom model for user. Uses email instead of username for authentication.
    """
    username = None
    email = models.EmailField(verbose_name='email address', unique=True)
    first_name = models.CharField(verbose_name='first name', max_length=30)
    last_name = models.CharField(verbose_name='last name', max_length=50)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.get_full_name() or self.email


class Project(models.Model):
    title = models.CharField(max_length=30)
    participants = models.ManyToManyField(CustomUser, related_name='projects_as_participant')
    admins = models.ManyToManyField(CustomUser, related_name='projects_as_admin')

    def __str__(self):
        return self.title[:15]

    def get_absolute_url(self):
        return reverse('core:project_detail', kwargs={'project_pk': self.pk})


class Column(models.Model):
    title = models.CharField(max_length=30)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='columns')
    order = models.PositiveSmallIntegerField(db_index=True)

    class Meta:
        unique_together = ['project', 'order']
        ordering = ['order']

    def __str__(self):
        return self.title[:15]


class Task(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    performer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='tasks')
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title[:15]


class ChatMessage(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='messages')
    text = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='messages')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.author}: {self.text[:10]}'
