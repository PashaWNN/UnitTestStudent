import logging

from django.contrib.auth.models import Group, Permission


def get_student_group():
    group, _ = Group.objects.get_or_create(name='Студенты')
    group.permissions.clear()
    for model_name in ('task', 'solution'):
        codename = f'view_{model_name}'
        try:
            model_view_perm = Permission.objects.get(codename=codename)
        except Permission.DoesNotExist:
            logging.warning(f"Permission not found with codename '{codename}'.")
            continue
        group.permissions.add(model_view_perm)
    return group
