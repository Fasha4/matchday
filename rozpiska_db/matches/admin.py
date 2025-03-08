from django.contrib import admin
from .models import Name, Image, Sport, League, Team, Match, Channel_Type, Channel, Commentator, Broadcast

# Register your models here.
admin.site.register(Name)
admin.site.register(Image)
admin.site.register(Sport)
admin.site.register(League)
admin.site.register(Team)
admin.site.register(Match)
admin.site.register(Channel_Type)
admin.site.register(Channel)
admin.site.register(Commentator)
admin.site.register(Broadcast)
