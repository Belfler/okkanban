from django.dispatch import receiver
from django.db.models.signals import m2m_changed, pre_save

from core.models import Project, Column


@receiver(m2m_changed, sender=Project.admins.through)
def add_admin_to_participants(instance, action, reverse, pk_set, **kwargs):
    """
    Add user to participants after adding him to admins.
    """
    if action == 'post_add':
        project_ids, user_ids = ([instance.id], pk_set) if not reverse else (pk_set, [instance.id])
        for project in Project.objects.filter(id__in=project_ids):
            project.participants.add(*user_ids)


@receiver(m2m_changed, sender=Project.participants.through)
def remove_participant_from_admins(instance, action, reverse, pk_set, **kwargs):
    """
    Remove user from admins after removing him from participants.
    """
    if action in ('post_remove', 'post_clear'):
        project_ids, user_ids = ([instance.pk], pk_set) if not reverse else (pk_set, [instance.pk])
        for project in Project.objects.filter(id__in=project_ids):
            project.admins.remove(*user_ids)


@receiver(pre_save, sender=Column, dispatch_uid='test')
def change_neighbor_columns_order(instance, update_fields, **kwargs):
    """
    When creating or changing a column, increment or decrement order numbers of the same project's columns to solve
    collision.
    """
    if not Column.objects.filter(project_id=instance.project_id, order=instance.order).exists():
        # there is no column with such order number and no collision
        return

    project_id = instance.project_id
    if instance.pk:  # it's changing of an existing column
        current_order_number = Column.objects.get(pk=instance.pk).order
        new_order_number = instance.order
        if current_order_number == new_order_number:
            return
        instance.order = 0
        instance.save()

        if current_order_number < new_order_number:
            for column in Column.objects.filter(project_id=project_id,
                                                order__lte=new_order_number, order__gt=current_order_number):
                column.order -= 1
                column.save(update_fields=['order'])

        elif current_order_number > new_order_number:
            for column in Column.objects.filter(project_id=project_id, order__gte=new_order_number,
                                                order__lt=current_order_number).order_by('-order'):
                column.order += 1
                column.save(update_fields=['order'])

        instance.order = new_order_number
        instance.save(update_fields=['order'])

    else:  # it's creating of new column
        for column in Column.objects.filter(project_id=project_id,
                                            order__gte=instance.order).order_by('-order'):
            column.order += 1
            column.save(update_fields=['order'])
