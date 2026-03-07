from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'phone']
        widgets = {
            'phone': forms.TextInput(attrs={
                'placeholder': '(11) 99999-9999',
                'maxlength': '15'
            })
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("O nome do contato é obrigatório")
        if len(name) > 60:
            raise forms.ValidationError("O nome do contato deve ter menos de 60 caracteres")
        if len(name) < 3:
            raise forms.ValidationError("O nome do contato deve ter mais de 3 caracteres")
        return name
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("O telefone do contato é obrigatório")
        phone = phone.replace("(", "").replace(")", "").replace("-", "").replace(" ", "").replace("+", "")
        if len(phone) == 11 and not phone.startswith("55"):
            phone = "55" + phone
        if len(phone) != 13:
            raise forms.ValidationError("O formato do telefone do contato deve ser 55 (XX) XXXXX-XXXX")
        return phone