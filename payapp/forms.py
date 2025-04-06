from django import forms
from . import models


class PointsTransferForm(forms.ModelForm):
    class Meta:
        model = models.PointsTransfer
        fields = ["enter_destination_username", "enter_points_to_transfer"]


class PointsRequestForm(forms.ModelForm):
    class Meta:
        model = models.PointsRequest
        fields = ["enter_destination_username", "enter_points_to_transfer"]
