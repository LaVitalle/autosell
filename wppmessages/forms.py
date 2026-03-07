from django import forms
from .models import Message
from contacts.models import Contact
from products.models import Product
from categories.models import Category

class MessageForm(forms.ModelForm):
    send_type = forms.ChoiceField(
        choices=Message.TYPE_CHOICES, 
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white placeholder-neutral-500 dark:placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-neutral-500 dark:focus:ring-neutral-400 transition-colors duration-200',
            'onchange': 'toggleSendTypeFields()'
        })
    )
    
    contact = forms.ModelChoiceField(
        queryset=Contact.objects.all(), 
        required=True,
        empty_label="Selecione um contato",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white placeholder-neutral-500 dark:placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-neutral-500 dark:focus:ring-neutral-400 transition-colors duration-200'
        })
    )
    
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(), 
        required=False,
        empty_label="Selecione um produto",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white placeholder-neutral-500 dark:placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-neutral-500 dark:focus:ring-neutral-400 transition-colors duration-200'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), 
        required=False,
        empty_label="Selecione uma categoria",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white placeholder-neutral-500 dark:placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-neutral-500 dark:focus:ring-neutral-400 transition-colors duration-200'
        })
    )

    class Meta:
        model = Message
        fields = ['contact', 'product', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set form field requirements
        self.fields['contact'].required = True
        self.fields['send_type'].required = True
        
        # Set initial requirements based on form data
        data = kwargs.get('data')
        if data:
            send_type = data.get('send_type')
            if send_type == 'product':
                self.fields['product'].required = True
                self.fields['category'].required = False
            elif send_type == 'category':
                self.fields['product'].required = False
                self.fields['category'].required = True
        
    def clean(self):
        cleaned_data = super().clean()
        send_type = cleaned_data.get('send_type')
        product = cleaned_data.get('product')
        category = cleaned_data.get('category')
        
        if send_type == 'product' and not product:
            raise forms.ValidationError("Produto é obrigatório quando o tipo é 'Produto'.")
        elif send_type == 'category' and not category:
            raise forms.ValidationError("Categoria é obrigatória quando o tipo é 'Categoria'.")
            
        return cleaned_data