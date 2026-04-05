from django.contrib import admin

from .models import Agent, KnowledgeBase, Priority, Status, Ticket, TicketComment, TicketHistory


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
	list_display = ("id", "name")
	search_fields = ("name",)


@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "level")
	ordering = ("level",)
	search_fields = ("name",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "customer", "status", "priority", "created_at")
	list_filter = ("status", "priority", "created_at")
	search_fields = ("title", "description", "customer__username")
	autocomplete_fields = ("customer", "status", "priority")


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
	list_display = ("id", "ticket", "user", "created_at")
	list_filter = ("created_at",)
	search_fields = ("comment_text", "ticket__title", "user__username")
	autocomplete_fields = ("ticket", "user")


@admin.register(TicketHistory)
class TicketHistoryAdmin(admin.ModelAdmin):
	list_display = ("id", "ticket", "status", "actor", "changed_at")
	list_filter = ("status", "changed_at")
	autocomplete_fields = ("ticket", "status", "actor")


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "department", "availability")
	list_filter = ("availability", "department")
	search_fields = ("user__username", "department")
	autocomplete_fields = ("user",)


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
	list_display = ("id", "title", "category")
	list_filter = ("category",)
	search_fields = ("title", "content", "tags")
