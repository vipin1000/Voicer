from django.contrib import admin
from .models import*

admin.site.register(UserProfile)
admin.site.register(VoiceoverService)
admin.site.register(Order)
admin.site.register(ChatMessage)
admin.site.register(Review)
