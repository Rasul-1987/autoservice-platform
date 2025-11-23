from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Autoservice


class AutoserviceRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=20, required=True, label='Телефон')
    location = forms.CharField(max_length=255, required=True, label='Адрес',
                               widget=forms.TextInput(attrs={
                                   'id': 'address-input',
                                   'placeholder': 'Введите адрес для отображения на карте'
                               }))
    cat_branch = forms.CharField(max_length=100, required=True, label='Категория услуг')
    type_of_verificating = forms.ChoiceField(
        choices=Autoservice.VERIFICATION_TYPES,
        initial='basic',
        label='Тип верификации'
    )

    # Скрытые поля для координат
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'location', 'cat_branch',
                  'type_of_verificating', 'latitude', 'longitude', 'password1', 'password2']

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
            Autoservice.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                email=self.cleaned_data['email'],
                location=self.cleaned_data['location'],
                cat_branch=self.cleaned_data['cat_branch'],
                type_of_verificating=self.cleaned_data['type_of_verificating'],
                latitude=self.cleaned_data['latitude'],
                longitude=self.cleaned_data['longitude']
            )
        return user

class AutoserviceProfileForm(forms.ModelForm):
    """Форма для редактирования профиля автосервиса"""
    class Meta:
        model = Autoservice
        fields = ['phone', 'email', 'location', 'cat_branch', 'type_of_verificating']