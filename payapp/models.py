from django.contrib.auth.models import User
from django.db import models


class Points(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.FloatField(default=1000)
    p_type = (
            ('GB Pounds','GB Pounds'),
            ('US dollars', 'US dollars'),
            ('Euros','Euros')
            )
    points_type = models.CharField(max_length=12, choices=p_type, default='GB Pounds')
    def __str__(self):
        details = ''
        details += f'Username     : {self.name}\n'
        details += f'Points       : {self.points}\n'
        details += f'Points_type  : {self.points_type}\n'
        return details


class PointsTransfer(models.Model):
    enter_your_username = models.CharField(max_length=50)
    enter_destination_username = models.CharField(max_length=50)
    enter_points_to_transfer = models.FloatField()
    points_type = models.CharField(max_length=50)
    date_time = models.CharField(max_length=100)

    def __str__(self):
        details = ''
        details += f'Your username            : {self.enter_your_username}\n'
        details += f'Destination username     : {self.enter_destination_username}\n'
        details += f'Points To Transfer         : {self.enter_points_to_transfer}\n'
        details += f'Points type           : {self.points_type}\n'
        return details

class PointsRequest(models.Model):
    enter_your_username = models.CharField(max_length=50)
    enter_destination_username = models.CharField(max_length=50)
    enter_points_to_transfer = models.FloatField()
    points_type = models.CharField(max_length=50)
    status = (
        ('Pending','Pending'),
        ('Approved', 'Approved'),
        ('Rejected','Rejected')
    )
    transfer_status = models.CharField(max_length=12, choices=status, default='Pending')
    date_time = models.CharField(max_length=100)


    def __str__(self):
        details = ''
        details += f'Your username            : {self.enter_your_username}\n'
        details += f'Destination username     : {self.enter_destination_username}\n'
        details += f'Points To Transfer         : {self.enter_points_to_transfer}\n'
        details += f'Points type           : {self.points_type}\n'
        return details