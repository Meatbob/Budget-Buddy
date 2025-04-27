from ast import Import
from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils.timezone import now

class Item(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class Expense(models.Model):
    CATEGORY_CHOICES = sorted([
    ('Food', 'Food'),
    ('Transport', 'Transport'),
    ('Entertainment', 'Entertainment'),
    ('Utilities', 'Utilities'),
    ('Others', 'Others'),
    ('Housing', 'Housing'),
    ('Health', 'Health'),
    ('Insurance', 'Insurance'),
    ('Education', 'Education'),
    ('Savings', 'Savings'),
    ('Debt', 'Debt'),
    ('Personal Care', 'Personal Care'),
    ('Gifts', 'Gifts'),
    ('Shopping', 'Shopping'),
    ('Subscriptions', 'Subscriptions'),
    ('Taxes', 'Taxes'),
    ('Business Expenses', 'Business Expenses'),
    ('Travel', 'Travel'),
    ('Home Maintenance', 'Home Maintenance'),
    ('Pets', 'Pets'),
], key=lambda x: x[0])

    TYPE_CHOICES = [
        ('Expense', 'Expense'),
        ('Income', 'Income')
    ]
    
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Others')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='Expense')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - {self.amount}"
    
class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    # month = models.IntegerField()
    # year = models.IntegerField(default=now().year)

    def __str__(self):
        return f"{self.user.username} - {self.category}: ${self.limit}"
