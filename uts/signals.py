from django.db.models.signals import post_save
from django.dispatch import receiver

from uts.models import Solution
from uts.tasks import run_solution


@receiver(post_save, sender=Solution)
def _run_sandbox_callback(sender, instance: Solution, **__):
    if instance.state == Solution.NEW:
        run_solution(instance.pk)


ready = False
