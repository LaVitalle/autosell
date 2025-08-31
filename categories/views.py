from django.shortcuts import render
from .models import Category

# Create your views here.
def get_all_categories(request):
    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories})