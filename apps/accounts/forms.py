from django import forms

class CustomSignupForm(forms.Form):
    phone_number = forms.CharField(
        max_length=20,
        label='Phone Number',
        widget=forms.TextInput(attrs={'placeholder': '+1 (555) 000-0000', 'type': 'tel'})
    )

    def signup(self, request, user):
        user.userprofile.phone_number = self.cleaned_data['phone_number']
        user.userprofile.save()
