from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Money(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    money = models.FloatField(default=1000)
    p_type = (
        ('GB Pounds', 'GB Pounds'),
        ('US dollars', 'US dollars'),
        ('Euros', 'Euros')
    )
    money_type = models.CharField(max_length=12, choices=p_type, default='GB Pounds')

    def __str__(self):
        details = ''
        details += f'Username     : {self.name.username}\n'
        details += f'Money        : {self.money}\n'
        details += f'Money_type   : {self.money_type}\n'
        return details

class MoneyTransfer(models.Model):
    enter_your_username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_moneytransfers')
    enter_destination_username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_moneytransfers')
    enter_money_to_transfer = models.FloatField()
    money_type = models.CharField(max_length=50)
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        details = ''
        details += f'Your username            : {self.enter_your_username.username}\n'
        details += f'Destination username     : {self.enter_destination_username.username}\n'
        details += f'Money To Transfer         : {self.enter_money_to_transfer}\n'
        details += f'Money type               : {self.money_type}\n'
        return details

class MoneyRequest(models.Model):
    enter_your_username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_moneyrequests')
    enter_destination_username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_moneyrequests')
    enter_money_to_transfer = models.FloatField()
    money_type = models.CharField(max_length=50)
    status = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    )
    transfer_status = models.CharField(max_length=12, choices=status, default='Pending')
    date_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        details = ''
        details += f'Your username            : {self.enter_your_username.username}\n'
        details += f'Destination username     : {self.enter_destination_username.username}\n'
        details += f'Money To Transfer         : {self.enter_money_to_transfer}\n'
        details += f'Money type               : {self.money_type}\n'
        return details
