from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Client, RepairRequest


class ClientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=20, required=True, label='Телефон')
    location = forms.CharField(max_length=255, required=True, label='Местоположение')

    car_brand = forms.CharField(max_length=100, required=False, label='Марка автомобиля')
    car_model = forms.CharField(max_length=100, required=False, label='Модель автомобиля')
    car_year = forms.IntegerField(required=False, label='Год выпуска')
    car_vin = forms.CharField(max_length=17, required=False, label='VIN код')
    car_license_plate = forms.CharField(max_length=15, required=False, label='Госномер')



    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'location', 'car_brand', 'car_model',
                  'car_year', 'car_vin', 'car_license_plate', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            client = Client.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                email=self.cleaned_data['email'],
                location=self.cleaned_data['location'],
                car_brand=self.cleaned_data['car_brand'],
                car_model=self.cleaned_data['car_model'],
                car_year=self.cleaned_data['car_year'],
                car_vin=self.cleaned_data['car_vin'],
                car_license_plate=self.cleaned_data['car_license_plate']
            )
        return user


class RepairRequestForm(forms.ModelForm):
    class Meta:
        model = RepairRequest
        fields = ['title', 'description', 'desired_price', 'photo']  # Убрали autoservice
        widgets = {
            'description': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Подробно опишите проблему с автомобилем...'}),
            'desired_price': forms.NumberInput(attrs={'placeholder': 'Необязательно'}),
            'title': forms.TextInput(attrs={'placeholder': 'Краткое описание проблемы'}),
        }
        labels = {
            'title': 'Заголовок заявки',
            'description': 'Описание проблемы',
            'desired_price': 'Желаемая стоимость (руб)',
            'photo': 'Фото проблемы',
        }

class ClientProfileForm(forms.ModelForm):
    """Форма для редактирования профиля клиента"""
    class Meta:
        model = Client
        fields = ['phone', 'email', 'location', 'car_brand', 'car_model', 'car_year', 'car_vin', 'car_license_plate']
        widgets = {
            'car_year': forms.NumberInput(attrs={'min': 1900, 'max': 2025}),
        }