from django.contrib import admin

# Register your models here.

from main.models import *


class PollingStationAdmin(admin.ModelAdmin):
	list_display = ['unique_id', 'name', 'sector_office', 'total_voters']
	search_fields = ('unique_id', 'name',)


class PresidingOfficerAdmin(admin.ModelAdmin):
	list_display = ['first_name', 'polling_station', 'mobile', 'second_mobile']
	search_fields = ('polling_station__unique_id', 'polling_station__name', 'first_name', 'mobile', 'second_mobile')


class PollUpdateAdmin(admin.ModelAdmin):
	list_display = ['polling_station', 'current_votes', 'time_field', 'timestamp']
	search_fields = ('polling_station__unique_id', 'polling_station__name', 'time_field', 'current_votes')


class POStatusAdmin(admin.ModelAdmin):
	list_display = ['presiding_officer', 'mock_poll_starts', 'mock_poll_resetted', 'mock_poll_ends', 'poll_starts',
	                'poll_ends']
	search_fields = ('presiding_officer__polling_station__unique_id', 'presiding_officer__polling_station__name',
	                 'presiding_officer__first_name')


admin.site.register(LAC)
admin.site.register(PollingStation, PollingStationAdmin)
admin.site.register(PresidingOfficer, PresidingOfficerAdmin)
admin.site.register(PollUpdate, PollUpdateAdmin)
admin.site.register(SectorOffice)
admin.site.register(POStatus, POStatusAdmin)
# admin.site.register(SOSUpdate)
# admin.site.register(EVM)
# admin.site.register(POLocation)
# admin.site.register(PSImage)
# admin.site.register(WebDevice)
# admin.site.register(Message)
admin.site.register(OtherDetails)
