from django.contrib import admin

from .models import Debt, Drinking, Participation, Drinks, Locations

# Register your models here.
admin.site.register(Debt)
admin.site.register(Drinking)
admin.site.register(Participation)
admin.site.register(Drinks)
admin.site.register(Locations)
