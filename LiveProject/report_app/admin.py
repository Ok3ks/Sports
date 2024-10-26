from django.contrib import admin
from report_app.models import GameweekScores
# Register your models here.
@admin.register(GameweekScores)
class GameweekScores(admin.ModelAdmin):
    list_display = (
        "index",
        # "from_user",
        # "to_user",
        # "conversation_id",
        # "sender_is_ai",
        # "message_text_markdown",  # Update this to display markdown version
        # "timestamp",
    )