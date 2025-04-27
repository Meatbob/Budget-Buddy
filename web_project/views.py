from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ExpenseForm, BudgetForm
from .models import Item, Expense, Budget
from django.contrib.auth import logout
from django.db.models import Sum
from django.http import HttpResponseForbidden
from datetime import datetime, date
from django.utils import timezone
from decimal import Decimal

def custom_logout(request):
    logout(request)
    return redirect('/login/')


@login_required
def category_summary(request):
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Get the selected month and year (defaults to current date if not provided)
    month = int(request.GET.get('month', current_month))  # Ensure it's an integer
    year = int(request.GET.get('year', current_year))  # Ensure it's an integer

    # Filter expenses for the selected month and year
    expenses = Expense.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month
    )

    # Calculate total income, total expenses, and balance for the selected month
    income_total = expenses.filter(type='Income').aggregate(total=Sum('amount'))['total'] or 0
    expense_total = expenses.filter(type='Expense').aggregate(total=Sum('amount'))['total'] or 0
    total_balance = income_total - expense_total

    # Get the total for each category for the selected month, including income and expenses
    categories = Expense.objects.filter(user=request.user, date__year=year, date__month=month).values('category').distinct()

    # Group expenses by category and calculate the net total for each category
    expenses_by_category = {}
    for category in categories:
        category_name = category['category']
        category_expenses = expenses.filter(category=category_name)

        income = category_expenses.filter(type='Income').aggregate(total=Sum('amount'))['total'] or 0
        expense = category_expenses.filter(type='Expense').aggregate(total=Sum('amount'))['total'] or 0
        net_total = income - expense  # Subtract expenses from income

        expenses_by_category[category_name] = {
            'total': net_total,
            'income': income,
            'expense': expense,
            'items': category_expenses,
        }

    # Get the list of available years for the dropdown
    years = Expense.objects.filter(user=request.user).dates('date', 'year')
    years = [year.year for year in years]

    # Get the month name directly based on the month number
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
    }
    month_name = month_names.get(month, "Invalid month")  # Get the month name or default to "Invalid month"

    return render(request, 'summary.html', {
        'income_total': income_total,
        'expense_total': expense_total,
        'total_balance': total_balance,
        'expenses_by_category': expenses_by_category,
        'month_name': month_name,
        'years': years,
        'selected_year': year,
        'month': month,
    })


# View for displaying the home page woth the total expenses
@login_required
def home(request):
    category_filter = request.GET.get('category', '')
    
    # Categories sorted alphabetically from the model
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
    ], key=lambda x: x[1])  # Sort by the category name (second value in tuple)

    # Filter expenses by category if applicable
    expenses = Expense.objects.filter(user=request.user)
    if category_filter:
        expenses = expenses.filter(category=category_filter)

    # Calculate totals for income and expenses
    income_total = expenses.filter(type='Income').aggregate(total=Sum('amount'))['total'] or 0
    expense_total = expenses.filter(type='Expense').aggregate(total=Sum('amount'))['total'] or 0
    balance = income_total - expense_total

    # Retrieve the most recent 10 expenses
    expenses = expenses.order_by('-date')[:10]

    # Initialize alerts for overspending
    alerts = []
    alert_message = check_budget_alert(request.user)

    if alert_message:
        alerts.extend(alert_message)

    # Get current date and filter budgets for the current month and year
    now = timezone.now()  # Use timezone-aware now to account for time zones
    current_month = now.month
    current_year = now.year

    # Debugging step: print current date
    print(f"Debug: Current month is {current_month}, year is {current_year}")

    try:
        budgets = Budget.objects.filter(user=request.user, month=current_month, year=current_year)
    except Exception as e:
        print(f"Error in filtering budgets: {str(e)}")
        budgets = []

    # Debugging step: print filtered budgets
    print(f"Debug: Found {len(budgets)} budgets for user {request.user}")

    # Check if overspending alerts should be shown
    for budget in budgets:
        print(f"Debug: Checking budget for category {budget.category} with limit {budget.amount}")

        spent = Expense.objects.filter(
            user=request.user,
            category=budget.category,
            type='Expense',
            date__month=current_month,
            date__year=current_year
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Debugging step: print spent amount
        print(f"Debug: Spent {spent} on category {budget.category}")

        # If 90% or more of the budget is used, show an alert
        if spent >= budget.limit * 0.9:
            alerts.append(f"You're close to reaching your limit for {budget.category} (${spent} of ${budget.limit})")

    return render(request, 'home.html', {
        'expenses': expenses,
        'total_expenses': balance,
        'income_total': income_total,
        'expense_total': expense_total,
        'category_filter': category_filter,
        'category_choices': CATEGORY_CHOICES,  # Pass the sorted category choices to the template
        'alert_message': alert_message,
        'alerts': alerts,
    })

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    return redirect('home')
    
# View for adding a new expense
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user # Associate the expense with the logged-in user
            expense.save()
            return redirect('home')
    else:
        form = ExpenseForm()
    return render(request, 'add_expense.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}! You can now log in.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form':form})

@login_required
def item_list(request):
    items = Item.objects.filter(created_by=request.user)
    return render(request, 'core/item_list.html', {'items': items})

@login_required
def item_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        Item.objects.create(title=title, description=description, created_by=request.user)
        return redirect('item_list')
    return render(request, 'core/item_form.html')

@login_required
def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk, created_by=request.user)
    if request.method == 'POST':
        item.title = request.POST.get('title')
        item.description = request.POST.get('description')
        item.save()
        return redirect('item_list')
    return render(request, 'core/item_form.html', {'item': item})

@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk, created_by=request.user)
    item.delete()
    return redirect('item_list')

def public_home(request):
    return render(request, 'core/public_home.html')

@login_required
def set_budget(request):
    # Define the categories that will be displayed in the dropdown menu
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
    ], key=lambda x: x[1])  # Sort categories alphabetically by name

    # Fetch existing budgets for the user
    budgets = Budget.objects.filter(user=request.user)

    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            # Check if a budget already exists for the selected category
            existing = Budget.objects.filter(user=request.user, category=budget.category).first()
            if existing:
                existing.limit = budget.limit
                existing.save()
            else:
                budget.save()
            messages.success(request, f"Budget for {budget.category} set!")
            return redirect('set_budget')
    else:
        form = BudgetForm()

    # Check for any budget alerts
    alert_message = check_budget_alert(request.user)

    # Pass the form, existing budgets, category choices, and alert message to the template
    return render(request, 'set_budget.html', {
        'form': form,
        'budgets': budgets,
        'category_choices': CATEGORY_CHOICES,
        'alert_message': alert_message,  # Pass alert message to the template
    })

def check_budget_alert(user):
    budgets = Budget.objects.filter(user=user)
    alert_messages = []  # Initialize an empty list to store alert messages

    for budget in budgets:
        total_expenses = Expense.objects.filter(user=user, category=budget.category).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        # Check if user is over budget (100% limit)
        if total_expenses >= budget.limit:
            alert_messages.append(f" ⚠️ Your {budget.category} budget has been exceeded!")

        # Check if user is over 90% of budget
        elif total_expenses >= budget.limit * Decimal('0.9'):
            alert_messages.append(f" ⚠️ You have used over 90% of your {budget.category} budget!")

    return alert_messages