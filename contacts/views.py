from django.shortcuts import render, get_object_or_404, redirect
from .models import Contact
from .forms import ContactForm
# Create your views here.
def get_all_contacts(request):
    contacts = Contact.objects.all()
    context = {
        'contacts': contacts,
    }
    return render(request, 'contacts.html', context)

def create_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('get_all_contacts')
    else:
        form = ContactForm()
    return render(request, 'create_contact.html', {'form': form})

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

def delete_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    if request.method == 'POST' and request.POST['_method'] == 'DELETE':
        contact.delete()
        return redirect('get_all_contacts')
    else:
        return render(request, 'confirm_delete_contact.html', {'contact': contact})