from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Contact
from .forms import ContactForm


@login_required
def get_all_contacts(request):
    return render(request, 'contacts.html')

@login_required
def create_contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('get_all_contacts')
    else:
        form = ContactForm()
    return render(request, 'contact_form.html', {
        'form': form,
        'is_edit': False,
        'contact': None,
        'page_title': 'Criar Contato',
        'page_subtitle': 'Adicione um novo contato ao sistema',
        'submit_label': 'Criar Contato',
    })

@login_required
def edit_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    context = {
        'contact': contact,
        'is_edit': True,
        'page_title': 'Editar Contato',
        'page_subtitle': 'Atualize as informações do contato',
        'submit_label': 'Salvar Alterações',
    }
    if request.method == 'POST':
        form = ContactForm(request.POST or None, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('get_all_contacts')
    else:
        form = ContactForm(instance=contact)
    context['form'] = form
    return render(request, 'contact_form.html', context)

@login_required
def delete_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    if request.method == 'POST' and request.POST['_method'] == 'DELETE':
        contact.delete()
        return redirect('get_all_contacts')
    else:
        return render(request, 'confirm_delete_contact.html', {'contact': contact})
