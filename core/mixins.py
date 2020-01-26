from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.urls import reverse

from core.forms import ColumnForm, TaskForm
from core.models import Column, Task


class ProjectParticipationRequiredMixin(AccessMixin):
    """
    Verify that the current user is participant of the project.
    """
    project_pk_url_kwarg = 'project_pk'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.projects_as_participant.filter(pk=self.kwargs.get(self.project_pk_url_kwarg)).exists():
            self.handle_no_permission()
        return super(ProjectParticipationRequiredMixin, self).dispatch(request, *args, **kwargs)


class ProjectAdministrationRequiredMixin(AccessMixin):
    """
    Verify that the current user is admin of the project.
    """
    project_pk_url_kwarg = 'project_pk'
    extra_context = {'is_admin': True}

    def dispatch(self, request, *args, **kwargs):
        if not request.user.projects_as_admin.filter(pk=self.kwargs.get(self.project_pk_url_kwarg)).exists():
            self.handle_no_permission()
        return super(ProjectAdministrationRequiredMixin, self).dispatch(request, *args, **kwargs)


class ColumnProcessMixin:
    """
    Define general attributes for work with columns. Project participation is required.
    """
    model = Column
    form_class = ColumnForm
    pk_url_kwarg = 'column_pk'
    template_name = 'core/form.html'
    project_pk_url_kwarg = 'project_pk'
    success_message = None

    def get_success_message(self):
        return self.success_message

    def get_form_kwargs(self):
        kwargs = super(ColumnProcessMixin, self).get_form_kwargs()
        kwargs['project_pk'] = self.kwargs[self.project_pk_url_kwarg]
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs.update({'project_pk': self.kwargs[self.project_pk_url_kwarg]})
        return super(ColumnProcessMixin, self).get_context_data(**kwargs)

    def get_success_url(self):
        if success_message := self.get_success_message():
            messages.success(self.request, success_message)
        return reverse('core:project_detail', kwargs={'project_pk': self.kwargs[self.project_pk_url_kwarg]})


class TaskProcessMixin:
    """
    Define general attributes for work with tasks. Project participation is required.
    """
    model = Task
    form_class = TaskForm
    pk_url_kwarg = 'task_pk'
    template_name = 'core/form.html'
    project_pk_url_kwarg = 'project_pk'
    success_message = None

    def get_success_message(self):
        return self.success_message

    def get_form_kwargs(self):
        kwargs = super(TaskProcessMixin, self).get_form_kwargs()
        kwargs['project_pk'] = self.kwargs[self.project_pk_url_kwarg]
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs.update({'project_pk': self.kwargs[self.project_pk_url_kwarg]})
        return super(TaskProcessMixin, self).get_context_data(**kwargs)

    def get_success_url(self):
        if success_message := self.get_success_message():
            messages.success(self.request, success_message)
        return reverse('core:project_detail', kwargs={'project_pk': self.kwargs[self.project_pk_url_kwarg]})
