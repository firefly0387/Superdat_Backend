
from django.contrib import admin
from product.submodules.order.models import (
   Order
   )
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'address','total_amount', 'unread_indicator', 'ordered_at']
    list_filter = ('ordered_at', 'unread')
    actions = ['mark_as_read']

    def unread_indicator(self, obj):
        if obj.unread:
            # Jazzmin respects admin CSS – so HTML works
            return '🔴'
        return '✅'
    unread_indicator.short_description = "Status"

    def mark_as_read(self, request, queryset):
        updated = queryset.update(unread=False)
        self.message_user(request, f"{updated} package(s) marked as read.")
    mark_as_read.short_description = "Mark selected as read"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and obj.unread:
            obj.unread = False
            obj.save()
        return super().change_view(request, object_id, form_url, extra_context)