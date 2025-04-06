from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from payapp.models import Points

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    p_type = [
                ('GB Pounds','GB Pounds'),
                ('US dollars', 'US dollars'),
                ('Euros','Euros')
    ]
    points_type = forms.ChoiceField(choices=p_type, widget=forms.Select)

    class Meta:
        model = User
        fields = ("username","first_name", "last_name", "email", "password1", "password2", "points_type")

    @staticmethod
    def conversion(src_type, dst_type, points):
        conversion_rates = {
        'GB Pounds': {'US dollars': 1.24, 'Euros': 1.16},
        'US dollars': {'GB Pounds': 1 / 1.24, 'Euros': 1.16 / 1.24},
        'Euros': {'GB Pounds': 1 / 1.16, 'US dollars': 1.24 / 1.16}
        }

        if src_type == dst_type:
            # No conversion needed
            return points
        elif src_type in conversion_rates and dst_type in conversion_rates[src_type]:
            # Conversion between different currency types
            conversion_rate = conversion_rates[src_type][dst_type]
            return points * conversion_rate
        else:
            # Unsupported currency types
            raise ValueError("Unsupported currency conversion")


    print(points_type)
    def save(self, *args, **kwargs):
        instance = super(RegisterForm, self).save(*args, **kwargs)
        currency_type = self.cleaned_data['points_type']
        default_currency_type = "GB Pounds"
        points = self.conversion(default_currency_type, currency_type, 1000)
        Points.objects.create(name=instance, points=points, points_type=currency_type)
        return instance