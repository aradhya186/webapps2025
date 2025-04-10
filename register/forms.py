from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from payapp.models import Money

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    p_type = [
                ('GB Pounds','GB Pounds'),
                ('US dollars', 'US dollars'),
                ('Euros','Euros')
    ]
    money_type = forms.ChoiceField(choices=p_type, widget=forms.Select)

    class Meta:
        model = User
        fields = ("username","first_name", "last_name", "email", "password1", "password2", "money_type")

    @staticmethod
    def conversion(src_type, dst_type, money):
        conversion_rates = {
        'GB Pounds': {'US dollars': 1.24, 'Euros': 1.16},
        'US dollars': {'GB Pounds': 1 / 1.24, 'Euros': 1.16 / 1.24},
        'Euros': {'GB Pounds': 1 / 1.16, 'US dollars': 1.24 / 1.16}
        }

        if src_type == dst_type:
            # No conversion needed
            return money
        elif src_type in conversion_rates and dst_type in conversion_rates[src_type]:
            # Conversion between different currency types
            conversion_rate = conversion_rates[src_type][dst_type]
            return money * conversion_rate
        else:
            # Unsupported currency types
            raise ValueError("Unsupported currency conversion")


    print(money_type)
    def save(self, *args, **kwargs):
        instance = super(RegisterForm, self).save(*args, **kwargs)
        currency_type = self.cleaned_data['money_type']
        default_currency_type = "GB Pounds"
        money = self.conversion(default_currency_type, currency_type, 1000)
        money.objects.create(name=instance, money=money, money_type=currency_type)
        return instance