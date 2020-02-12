import os
from uuid import uuid4

from redis import StrictRedis
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView, DetailView, CreateView, FormView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect

from core.mixins import (ProjectParticipationRequiredMixin, ColumnProcessMixin, TaskProcessMixin,
                         ProjectAdministrationRequiredMixin)
from core.models import CustomUser, Project
from core.forms import ProjectForm, CustomUserCreationForm, InvitationForm
from core.tasks import send_mail_async
from core.utils import Button

redis_db = StrictRedis.from_url(os.environ['REDIS_URL'], db=1, decode_responses=True)


class Summary(LoginRequiredMixin, TemplateView):
    template_name = 'core/summary.html'


class ProjectCreation(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'core/form.html'
    form_class = ProjectForm
    extra_context = {
        'page_title': 'Creating of new project',
        'main_button': Button(text='Create'),
    }

    def form_valid(self, form):
        project = form.save()
        project.admins.add(self.request.user)
        messages.success(self.request, f'The project "{project.title}" has been successfully created.')
        return super(ProjectCreation, self).form_valid(form)


class ProjectDetail(ProjectParticipationRequiredMixin, DetailView):
    model = Project
    template_name = 'core/project_detail.html'
    pk_url_kwarg = 'project_pk'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        kwargs.update({
            'project_pk': self.get_object().pk,
            'is_admin': self.request.user in self.get_object().admins.all()
        })
        return super(ProjectDetail, self).get_context_data(**kwargs)


class ProjectSettings(ProjectAdministrationRequiredMixin, UpdateView):
    model = Project
    template_name = 'core/form.html'
    form_class = ProjectForm
    pk_url_kwarg = 'project_pk'
    extra_context = {
        'page_title': 'Project settings',
        'main_button': Button(text='Save'),
    }

    def get_context_data(self, **kwargs):
        project_deletion_url = reverse('core:project_deletion', kwargs={'project_pk': self.get_object().pk})
        deletion_button = Button(text='Delete', url=project_deletion_url, is_warning=True)
        kwargs.update({
            'project_pk': self.get_object().pk,
            'extra_buttons': [deletion_button],
        })
        return super(ProjectSettings, self).get_context_data(**kwargs)

    def get_success_url(self):
        messages.success(self.request, f'Settings of the project "{self.get_object().title}" '
                                       f'has been successfully saved.')
        return self.get_object().get_absolute_url()


class ProjectLeave(ProjectParticipationRequiredMixin, DetailView):
    model = Project
    template_name = 'core/form.html'
    pk_url_kwarg = 'project_pk'
    context_object_name = 'project'
    extra_context = {
        'page_title': 'Leaving Project',
        'main_button': Button(text='Leave', is_warning=True),
    }

    def get_context_data(self, **kwargs):
        project = self.get_object()
        extra_text = 'Are you sure?'
        if project.participants.count() == 1:
            extra_text += ' As you are the only participant, after your leaving the ' \
                          'project will be deleted.'
        kwargs.update({
            'extra_text': extra_text,
            'project_pk': project.pk,
        })
        return super(ProjectLeave, self).get_context_data(**kwargs)

    def get_success_url(self):
        messages.success(self.request, f'You have successfully left the project "{self.get_object().title}".')
        return reverse('core:summary')

    def post(self, request, *args, **kwargs):
        project = self.get_object()
        success_url = self.get_success_url()
        if project.participants.count() == 1:
            project.delete()
        else:
            project.participants.remove(self.request.user)
        return redirect(success_url)


class ProjectDeletion(ProjectAdministrationRequiredMixin, DeleteView):
    model = Project
    pk_url_kwarg = 'project_pk'
    template_name = 'core/form.html'
    extra_context = {
        'page_title': 'Deletion of the project',
        'extra_text': 'Are you sure?',
        'main_button': Button(text='Delete', is_warning=True),
    }

    def get_context_data(self, **kwargs):
        kwargs.update({
            'project_pk': self.get_object().pk
        })
        return super(ProjectDeletion, self).get_context_data(**kwargs)

    def get_success_url(self):
        messages.success(self.request, f'The project "{self.get_object().title}" has been successfully deleted.')
        return reverse('core:summary')


class ColumnCreation(ProjectAdministrationRequiredMixin, ColumnProcessMixin, CreateView):
    extra_context = {
        'page_title': 'Creating of new column',
        'main_button': Button(text='Create'),
    }

    def get_success_message(self):
        return f'The column "{self.object.title}" has been successfully created.'

    def get_form_kwargs(self):
        kwargs = super(ColumnCreation, self).get_form_kwargs()
        kwargs['is_creation'] = True
        return kwargs

    def form_valid(self, form):
        column = form.save(commit=False)
        column.project_id = self.kwargs[self.project_pk_url_kwarg]
        column.save()
        return super(ColumnCreation, self).form_valid(form)


class ColumnChange(ProjectAdministrationRequiredMixin, ColumnProcessMixin, UpdateView):
    extra_context = {
        'page_title': 'Changing the column',
        'main_button': Button(text='Save'),
    }

    def get_success_message(self):
        return f'The column "{self.get_object().title}" has been successfully changed.'

    def get_context_data(self, **kwargs):
        column_deletion_url = reverse('core:column_deletion', kwargs={
            'project_pk': self.kwargs[self.project_pk_url_kwarg],
            'column_pk': self.kwargs[self.pk_url_kwarg]})
        deletion_button = Button(text='Delete', url=column_deletion_url, is_warning=True)
        kwargs.update({'extra_buttons': [deletion_button]})
        return super(ColumnChange, self).get_context_data(**kwargs)


class ColumnDeletion(ProjectAdministrationRequiredMixin, ColumnProcessMixin, DeleteView):
    extra_context = {
        'page_title': 'Deletion of the column',
        'extra_text': 'Are you sure?',
        'main_button': Button(text='Delete', is_warning=True),
    }

    def get_success_message(self):
        return f'The column "{self.get_object().title}" has been successfully deleted.'


class TaskCreation(ProjectParticipationRequiredMixin, TaskProcessMixin, CreateView):
    extra_context = {
        'page_title': 'Creation of new task',
        'main_button': Button(text='Create'),
    }

    def get_success_message(self):
        return f'The task "{self.object.title}" has been successfully created.'


class TaskChange(ProjectParticipationRequiredMixin, TaskProcessMixin, UpdateView):
    extra_context = {
        'page_title': 'Changing the task',
        'main_button': Button(text='Save'),
    }

    def get_success_message(self):
        return f'The task "{self.get_object().title}" has been successfully changed.'

    def get_context_data(self, **kwargs):
        task_deletion_url = reverse('core:task_deletion', kwargs={
            'project_pk': self.kwargs[self.project_pk_url_kwarg],
            'task_pk': self.kwargs[self.pk_url_kwarg]})
        deletion_button = Button(text='Delete', url=task_deletion_url, is_warning=True)
        kwargs.update({'extra_buttons': [deletion_button]})
        return super(TaskChange, self).get_context_data(**kwargs)


class TaskDeletion(ProjectParticipationRequiredMixin, TaskProcessMixin, DeleteView):
    extra_context = {
        'page_title': 'Deletion of the task',
        'extra_text': 'Are you sure?',
        'main_button': Button(text='Delete', is_warning=True),
    }

    def get_success_message(self):
        return f'The task "{self.object.title}" has been successfully deleted.'


class Invitation(ProjectParticipationRequiredMixin, FormView):
    form_class = InvitationForm
    template_name = 'core/form.html'
    extra_context = {
        'page_title': 'Invitation of new person',
        'main_button': Button(text='Send Invitation'),
    }

    def get_context_data(self, **kwargs):
        kwargs.update({'project_pk': self.kwargs['project_pk']})
        return super(Invitation, self).get_context_data(**kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']

        if not CustomUser.objects.filter(email=email).exists():
            messages.error(self.request, 'There is no user with such email.')

        else:
            uuid = str(uuid4())
            invited_user_pk = CustomUser.objects.get(email=email).pk
            project_pk = self.kwargs[self.project_pk_url_kwarg]
            redis_db.set(f'user:{invited_user_pk}:project:{project_pk}', uuid, ex=86400 * 3)
            url_to_join = self.request.build_absolute_uri(reverse('core:join_project',
                                                                  kwargs={'project_pk': project_pk, 'uuid': uuid}))
            send_mail_async.delay(
                'Invitation',
                f'You are invited in the project "{Project.objects.get(pk=project_pk).title}". '
                f'Click {url_to_join} to join.',
                os.environ['EMAIL_HOST_USER'],
                [email]
            )
            messages.success(self.request, 'The invitation has been successfully sent.')

        return super(Invitation, self).form_valid(form)

    def get_success_url(self):
        return self.request.get_full_path()


class JoiningProject(LoginRequiredMixin, View):
    project_pk_url_kwarg = 'project_pk'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:login')

        user_pk = request.user.pk
        project_pk = self.kwargs[self.project_pk_url_kwarg]
        redis_key = f'user:{user_pk}:project:{project_pk}'
        saved_uuid = redis_db.get(redis_key)
        current_uuid = str(self.kwargs['uuid'])

        if saved_uuid == current_uuid:
            Project.objects.get(pk=project_pk).participants.add(user_pk)
            messages.success(request, 'You have successfully joined the project.')
            redis_db.delete(redis_key)
            return redirect('core:project_detail', project_pk=project_pk)

        else:
            messages.error(request, 'You cannot join the project. The link is probably out of date.')
            return redirect('core:summary')


class Login(LoginView):
    template_name = 'core/form.html'
    extra_context = {
        'page_title': 'Login',
        'main_button': Button(text='Log In'),
    }

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(Login, self).get(request, *args, **kwargs)


class Registration(FormView):
    form_class = CustomUserCreationForm
    template_name = 'core/form.html'
    extra_context = {
        'page_title': 'Registration',
        'main_button': Button(text='Sign Up'),
    }
    success_url = reverse_lazy('core:summary')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(Registration, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Now you can be invited to a project or create your own.')
        return super(Registration, self).form_valid(form)
