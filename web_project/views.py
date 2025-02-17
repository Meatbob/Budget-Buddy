from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ExpenseForm
from .models import Item, Expense
from django.contrib.auth import logout
from django.db.models import Sum
from django.http import HttpResponseForbidden

def custom_logout(request):
    logout(request)
    return redirect('/login/')

def category_summary(request):
    if request.user.is_authenticated:
        category_totals = (
            Expense.objects.filter(user=request.user)
            .values('category')
            .annotate(total=Sum('amount'))
            .order_by('category')
        )
        return render(request, 'category_summary.html', {'category_totals': category_totals})
    else:
        return redirect('login')

# View for displaying the home page woth the total expenses
@login_required
def home(request):
    category_filter = request.GET.get('category', '')
    if category_filter:
        expenses = Expense.objects.filter(user=request.user, category=category_filter)
    else:
        expenses = Expense.objects.filter(user=request.user)
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'home.html', {'expenses': expenses, 'total_expenses': total_expenses, 'category_filter': category_filter})


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
