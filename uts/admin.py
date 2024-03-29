from functools import update_wrapper

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.utils import unquote
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import PermissionDenied
from django.forms import forms
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from uts.models import Task, Solution, User, Environment
from uts.utils import get_student_group


class MyAdminSite(admin.AdminSite):
    site_title = 'UnitTestStudent'
    site_header = 'UnitTestStudent'
    index_title = ' '
    site_url = None

    def app_index(self, request, app_label, extra_context=None):
        response: TemplateResponse = super().app_index(request, app_label, extra_context)
        response.context_data['title'] = None
        return response


admin_site = MyAdminSite()


class CustomUserAdmin(UserAdmin):
    view_on_site = False
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_student',),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = 'last_login', 'date_joined'

    def save_model(self, request, obj: User, form, change):
        obj.is_staff = True
        super().save_model(request, obj, form, change)


admin_site.register(User, UserAdmin)


class TaskStateFilter(SimpleListFilter):
    title = 'Статус задачи'

    parameter_name = 'taskstate'
    CHECKED = 'Зачтённые'
    UNCHECKED = 'Незачтённые'
    SOLVED = 'Решённые'
    UNSOLVED = 'Нерешённые'

    def lookups(self, request, model_admin):
        if request.user.is_student:
            return [(item, item) for item in [self.CHECKED, self.UNCHECKED, self.SOLVED, self.UNSOLVED]]
        return []

    def queryset(self, request, queryset):
        if self.value() == self.CHECKED:
            return queryset.filter(solution__author=request.user, solution__checked=True)
        if self.value() == self.SOLVED:
            return queryset.filter(solution__author=request.user, solution__state=Solution.COMPLETED)
        if self.value() == self.UNSOLVED:
            return queryset.exclude(solution__author=request.user, solution__state=Solution.COMPLETED)
        if self.value() == self.UNCHECKED:
            return queryset.exclude(solution__author=request.user, solution__checked=True)


class TaskAdmin(admin.ModelAdmin):
    change_form_template = 'uts/admin_task_student_form.html'
    search_fields = 'name',
    list_filter = TaskStateFilter,

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update(dict(is_student=request.user.is_student))
        return super().render_change_form(request, context, add=add, change=change, form_url=form_url, obj=obj)

    def _changeform_view(self, request, object_id, form_url, extra_context):
        if '_upload-solution' in request.POST:
            return HttpResponseRedirect(reverse('admin:upload-solution', args=(object_id,)))
        return super()._changeform_view(request, object_id, form_url, extra_context)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        student_group = get_student_group()
        if request.user.groups.filter(pk=student_group.pk).count():
            remove_from_fieldsets(fieldsets, ('tests_file',))
        return fieldsets

    def get_urls(self):
        urls = super().get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        custom_urls = [
            path('<path:object_id>/solution_upload/', wrap(self.solution_upload_view), name='upload-solution'),
        ]

        return custom_urls + urls

    def solution_upload_view(self, request, object_id, extra_context=None):
        model = self.model
        obj = self.get_object(request, unquote(object_id))
        if obj is None:
            return self._get_obj_does_not_exist_redirect(request, model._meta, object_id)

        if not request.user.is_student:
            raise PermissionDenied

        opts = model._meta

        class SolutionUploadForm(forms.Form):
            file = forms.FileField(label='Файл с решением')

        if request.method == 'POST':
            form = SolutionUploadForm(request.POST, request.FILES)
            if form.is_valid():
                Solution.objects.filter(author=request.user, task=obj).delete()
                solution = Solution.objects.create(
                    task=obj,
                    author=request.user,
                    solution_file=form.cleaned_data['file'],
                    created_at=timezone.now()
                )
                url = reverse('admin:{}_{}_change'.format(
                    solution._meta.app_label,
                    solution._meta.model_name
                ), args=(solution.pk,))
                return HttpResponseRedirect(url)
        else:
            form = SolutionUploadForm()

        context = {
            **self.admin_site.each_context(request),
            'title': f'Загрузка решения для задачи {obj}',
            'form': form,
            'module_name': str(capfirst(opts.verbose_name_plural)),
            'object': obj,
            'opts': opts,
            'preserved_filters': self.get_preserved_filters(request),
            **(extra_context or {}),
        }

        request.current_app = self.admin_site.name

        return TemplateResponse(request, 'uts/solution_form.html', context)


admin_site.register(Task, TaskAdmin)


def remove_from_fieldsets(fieldsets, fields):
    for fieldset in fieldsets:
        for field in fields:
            if field in fieldset[1]['fields']:
                new_fields = []
                for new_field in fieldset[1]['fields']:
                    if not new_field in fields:
                        new_fields.append(new_field)

                fieldset[1]['fields'] = tuple(new_fields)
                break


class SolutionAdmin(admin.ModelAdmin):
    readonly_fields = 'created_at', 'log', 'author', 'task', 'state', 'solution_file'
    list_display = '__str__', 'state', 'checked', 'created_at'

    list_filter = 'author__username', 'checked', 'state', 'task__name'

    ordering = ('-created_at',)
    search_fields = 'author__username', 'author__first_name', 'author__last_name', 'task__name'

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_student:
            qs = qs.filter(author=request.user)
        return qs


admin_site.register(Solution, SolutionAdmin)



class EnvironmentAdmin(admin.ModelAdmin):
    list_display = 'name', 'docker_image'
    search_fields = 'name', 'docker_image'


admin_site.register(Environment, EnvironmentAdmin)
