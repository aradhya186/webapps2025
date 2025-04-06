import django.contrib

from .models import Points, PointsTransfer, PointsRequest
from django.contrib import admin

class points(admin.ModelAdmin):
    list_display = ['name','points', 'points_type']

class points_transfer(admin.ModelAdmin):
    list_display = ['enter_your_username','enter_destination_username', 'enter_points_to_transfer', 'points_type']

class points_request(admin.ModelAdmin):
    list_display = ['enter_your_username','enter_destination_username', 'enter_points_to_transfer', 'transfer_status', 'points_type']

admin.site.register(Points, points)
admin.site.register(PointsTransfer, points_transfer)
admin.site.register(PointsRequest, points_request)