from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.humanize.templatetags.humanize import ordinal

from core.models import CustomUser, Project, Column, Task


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password2'].help_text = None


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['email']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title']

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'autofocus': True})


class ColumnForm(forms.ModelForm):
    class Meta:
        model = Column
        fields = ['title', 'order']

    def __init__(self, project_pk, is_creation=False, *args, **kwargs):
        super(ColumnForm, self).__init__(*args, **kwargs)
        max_order_number = Project.objects.get(pk=project_pk).columns.count()
        if is_creation:
            max_order_number += 1
        choices = map(lambda elem: (elem, ordinal(elem)), range(1, max_order_number + 1))
        self.fields['order'].widget = forms.Select(choices=choices)
        self.fields['order'].initial = max_order_number
        self.fields['title'].widget.attrs.update({'autofocus': True})


class TaskForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), required=False)
    column = forms.ModelChoiceField(queryset=Column.objects.none(), empty_label=None)
    performer = forms.ModelChoiceField(queryset=CustomUser.objects.none(), required=False)

    class Meta:
        model = Task
        fields = ['title', 'description', 'column', 'performer']

    def __init__(self, project_pk, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['column'].queryset = Column.objects.filter(project=project_pk)
        self.fields['performer'].queryset = CustomUser.objects.filter(projects_as_participant=project_pk)
        self.fields['title'].widget.attrs.update({'autofocus': True})


class InvitationForm(forms.Form):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(InvitationForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'autofocus': True})
