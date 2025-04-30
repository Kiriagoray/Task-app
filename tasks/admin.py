from django.contrib import admin
from .models import Task
from .models import Team

admin.site.register(Task)
admin.site.register(Team)
