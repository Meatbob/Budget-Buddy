from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Expense, Budget

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Add an email field

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'date', 'category', 'type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'limit']
