from django.shortcuts import render
from contacts.models import Contact
from products.models import Product
from categories.models import Category

# Create your views here.
def messages_manager(request):
    context = {
        'contacts': Contact.objects.all(),
        'products': Product.objects.all(),
        'categories': Category.objects.all()
    }
    
    return render(request, 'messages_manager.html', context)