from django.contrib import admin
from .models import Note, Notification


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('note_title', 'created_at', 'updated_at', 'user')

admin.site.register(Notification)