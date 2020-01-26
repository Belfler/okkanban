from django import template
from django.urls import reverse

from core.models import ChatMessage, Project
from core.utils import Link

register = template.Library()


@register.inclusion_tag(filename='core/tags/chat.html')
def chat(project_pk):
    messages = ChatMessage.objects.filter(project_id=project_pk)
    return {'messages': messages, 'project_pk': project_pk}


@register.inclusion_tag(filename='core/tags/navigation.html', takes_context=True)
def navigation(context):
    links = [Link(text='OkKanban', url=reverse('core:summary'))]

    if project_pk := context.get('project_pk'):
        project_title = Project.objects.get(pk=project_pk).title
        project_detail_url = reverse('core:project_detail', kwargs={'project_pk': project_pk})
        links.append(Link(text=f'Project "{project_title}"', url=project_detail_url))

    if page_title := context.get('page_title'):
        links.append(Link(text=page_title, url=context.request.get_full_path()))

    return {'links': links}


@register.inclusion_tag(filename='core/tags/menu.html', takes_context=True)
def menu(context):
    links = []
    user = context.request.user

    if user.is_authenticated:
        links += [Link(text=user.get_full_name(), url=reverse('core:summary')),
                  Link(text='Log out', url=reverse('core:logout'))]
        if project_pk := context.get('project_pk'):
            links.append(Link(text='Leave Project',
                              url=reverse('core:project_leave', kwargs={'project_pk': project_pk})))

    else:
        links += [Link(text='Log In', url=reverse('core:login')),
                  Link(text='Sign Up', url=reverse('core:register'))]

    return {'links': links}
