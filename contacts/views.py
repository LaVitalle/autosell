from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Contact
from .forms import ContactForm
# Create your views here.
@login_required
def get_all_contacts(request):
    contacts_list = Contact.objects.all()
    paginator = Paginator(contacts_list, 12)
    page_number = request.GET.get('page')
    contacts = paginator.get_page(page_number)
    context = {
        'contacts': contacts,
    }
    return render(request, 'contacts.html', context)

@login_required
def create_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('get_all_contacts')
    else:
        form = ContactForm()
    return render(request, 'create_contact.html', {'form': form})

@login_required
def edit_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    if request.method == 'POST':
        form = ContactForm(request.POST or None, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('get_all_contacts')
    else:
        form = ContactForm(instance=contact)
    return render(request, 'edit_contact.html', {'form': form, 'contact': contact})

@login_required
def delete_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    if request.method == 'POST' and request.POST['_method'] == 'DELETE':
        contact.delete()
        return redirect('get_all_contacts')
    else:
        return render(request, 'confirm_delete_contact.html', {'contact': contact})