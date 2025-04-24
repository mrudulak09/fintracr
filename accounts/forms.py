from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, UserCreationForm
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from .models import Profile, CustomUser, SMSCode




class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'First Name'
        }),
        label=_('First Name'),
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Last Name'
        }),
        label=_('Last Name'),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Email'
        }),
        label=_('Email'),
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Phone Number'
        }),
        required=True,
        label=_('Phone Number'),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Password'
        }),
        label=_('Password'),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Confirm Password'
        }),
        label=_('Confirm Password'),
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            self.add_error('email', _('A user with this email already exists.'))

        return cleaned_data

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number or not phone_number.isdigit():
            raise forms.ValidationError(_('Please enter a valid phone number.'))
        return phone_number

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.username = self.cleaned_data['email']
        if commit:
            instance.save()
        return instance
    
    
    
class UpdateProfileForm(ModelForm):
    avatar = forms.ImageField(required=False)
    bio = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control form-control-user',
            'rows': 4,
            'placeholder': 'Enter your bio'
        }),
        max_length=1000,
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError(_('Email already exists.'))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        profile = user.profile
        if self.cleaned_data.get('avatar'):
            profile.avatar = self.cleaned_data['avatar']
        if self.cleaned_data.get('bio'):
            profile.bio = self.cleaned_data['bio']
        profile.save()
        return user

class Set_Password_Form(SetPasswordForm):
    class Meta:
        model = CustomUser
        fields = ['new_password1', 'new_password2']

class Password_Reset_Form(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SMSCodeForm(forms.ModelForm):
    number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Enter verification code'
        }),
        label=_('SMS Code')
    )

    class Meta:
        model = SMSCode
        fields = ['number']

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)

    def clean_number(self):
        num = self.cleaned_data.get('number')
        if not self.user_id:
            raise forms.ValidationError(_('Invalid user ID.'))
        try:
            user = CustomUser.objects.get(id=self.user_id)
        except CustomUser.DoesNotExist:
            raise forms.ValidationError(_('Invalid user ID.'))
        if num != str(user.smscode.number):
            raise forms.ValidationError(_('Invalid SMS verification code. Try again!'))
        return num
