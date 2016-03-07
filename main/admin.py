from django.contrib import admin

# Register your models here.

from main.models import *

admin.site.register(LAC)
admin.site.register(PollingStation)
admin.site.register(PresidingOfficer)
admin.site.register(PollUpdate)
admin.site.register(EmergencyContact)
admin.site.register(POStatus)
admin.site.register(SOSUpdate)
admin.site.register(EVM)
admin.site.register(POLocation)
admin.site.register(PSImage)
admin.site.register(WebDevice)
admin.site.register(Message)

