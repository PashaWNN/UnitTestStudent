from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from uts.models import Solution
from uts.tasks import run_solution


@receiver(post_save, sender=Solution)
def _run_sandbox_callback(sender, instance: Solution, **__):
    if instance.state == Solution.NEW:
        transaction.on_commit(lambda: run_solution.delay(instance.pk))


ready = False
