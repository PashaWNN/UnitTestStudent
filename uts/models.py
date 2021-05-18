from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from uts.utils import get_student_group


class User(AbstractUser):
    is_student = models.BooleanField(
        default=False,
        verbose_name='Студент',
        help_text='Пользователь, являющийся студентом может загружать решения,'
                  ' но не может просматривать среды выполнения и чужие решения'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        student_group = get_student_group()
        if self.is_student:
            self.groups.add(student_group)
        else:
            self.groups.remove(student_group)


class Environment(models.Model):
    name = models.CharField(max_length=512, verbose_name='Название', unique=True)
    description = models.TextField(
        verbose_name='Описание',
        help_text='Инструкция по использованию данной среды выполнения'
    )
    docker_image = models.CharField(max_length=512, verbose_name='Имя Docker-образа')
    command = models.CharField(max_length=512, verbose_name='Команда для запуска тестов')
    tests_filename = models.CharField(max_length=512, verbose_name='Имя файла с тестами')
    solution_filename = models.CharField(max_length=512, verbose_name='Имя файла-решения')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Среда выполнения'
        verbose_name_plural = 'среды выполнения'


class Task(models.Model):
    name = models.CharField(max_length=512, verbose_name='Название', unique=True)
    description = models.TextField(
        verbose_name='Описание задачи',
        help_text='Описание требований к задаче, а также того, в каком виде нужно загружать решение'
    )

    cpu_limit = models.PositiveSmallIntegerField(
        default=2,
        verbose_name='Ограничение процессорного времени',
        help_text='Ограничение реального времени будет в 5 раз выше ограничения процессорного'
    )
    memory_limit = models.PositiveSmallIntegerField(
        default=64,
        verbose_name='Ограничение объёма используемой ОЗУ (МБ)',
        help_text='Для всей среды выполнения, а не только для процесса тестов'
    )
    
    tests_file = models.FileField(
        upload_to='uploads',
        verbose_name='Файл с тестами для задачи'
    )
    environment = models.ForeignKey(
        to=Environment,
        on_delete=models.PROTECT,
        verbose_name='Среда выполнения'
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'задачи'

    def __str__(self):
        return self.name


class Solution(models.Model):
    NEW = 'NEW'
    RUNNING = 'RUN'
    FAILED = 'FAI'
    COMPLETED = 'COM'
    STATE_CHOICES = (
        (NEW, _('Добавлено')),
        (RUNNING, _('Выполняется')),
        (FAILED, _('Провалено')),
        (COMPLETED, _('Завершено успешно')),
    )

    solution_file = models.FileField(
        upload_to='uploads',
        verbose_name='Файл с решением',
    )
    task = models.ForeignKey(
        to=Task, on_delete=models.CASCADE,
        verbose_name='Задача',
    )
    author = models.ForeignKey(
        to=get_user_model(), on_delete=models.CASCADE,
        verbose_name='Автор решения',
    )
    state = models.CharField(
        max_length=3, choices=STATE_CHOICES, default=NEW,
        verbose_name='Состояние',
    )
    log = models.TextField(
        default='', blank=True,
        verbose_name='Лог',
    )

    created_at = models.DateTimeField(
        auto_created=True,
        verbose_name='Загружено',
    )

    checked = models.BooleanField(default=False, verbose_name='Зачтено')

    class Meta:
        verbose_name = 'Решение'
        verbose_name_plural = 'решения'

    def __str__(self):
        return f'Решение задачи "{self.task}" студентом {self.author}'
