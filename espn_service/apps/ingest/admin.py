"""Admin extensions for task scheduling."""

import json

from django.contrib import admin
from django_q.admin import ScheduleAdmin as BaseScheduleAdmin
from django_q.models import Schedule
from django_q.tasks import async_task


class ScheduleRunNowAdmin(BaseScheduleAdmin):
    """Extend Django-Q2's Schedule admin with a 'Run now' action."""

    actions = [*BaseScheduleAdmin.actions, "run_now"]

    @admin.action(description="Exécuter maintenant")
    def run_now(self, request, queryset):
        for schedule in queryset:
            args = json.loads(schedule.args) if schedule.args else []
            kwargs = json.loads(schedule.kwargs) if schedule.kwargs else {}
            async_task(schedule.func, *args, **kwargs)
            self.message_user(request, f"Tâche '{schedule.name}' enqueue.")


admin.site.unregister(Schedule)
admin.site.register(Schedule, ScheduleRunNowAdmin)
