# connector/admin.py

from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Count, Q
from .models import Message
from django.db.models.functions import TruncDate

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'datetime_send', 'datetime_got', 'done']
    change_list_template = "admin/connector/message_change_list.html"
    list_filter = ['datetime_send', 'datetime_got']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('daily-count/', self.admin_site.admin_view(self.daily_count_view), name='connector_message_daily_count'),
        ]
        return custom_urls + urls

    def daily_count_view(self, request):
        # Агрегируем количество отправленных и полученных сообщений по дате в одном запросе
        daily_counts = (
            Message.objects
            .annotate(day=TruncDate('datetime_send'))
            .values('day')
            .annotate(
                sent_count=Count('id', filter=Q(datetime_send__isnull=False)),
                received_count=Count('id', filter=Q(datetime_got__isnull=False))
            )
            .order_by('-day')
        )

        context = dict(
            self.admin_site.each_context(request),
            daily_counts=daily_counts,
            title='Messages Count per Day',
        )
        return TemplateResponse(request, "admin/connector/daily_count.html", context)