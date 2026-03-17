from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Full Name")
    email = forms.EmailField(required=True, help_text="This will be used for logging in.")
    department = forms.CharField(max_length=100, required=True)
    year_of_study = forms.IntegerField(required=True, min_value=1, max_value=5)
    
    class Meta:
        model = User
        fields = ('first_name', 'email', 'department', 'year_of_study')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        # Use email prefix as the internal username since Django requires it
        user.username = self.cleaned_data['email'].split('@')[0][:30] 
        
        if commit:
            user.save()
            # Create the associated UserProfile
            UserProfile.objects.create(
                user=user,
                department=self.cleaned_data['department'],
                year_of_study=self.cleaned_data['year_of_study']
            )
        return user
