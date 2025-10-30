from django import forms
from .models import Patient, CustomUser, Address

class PatientForm(forms.ModelForm):
    username = forms.CharField(label='username')
    cpf = forms.CharField(label='CPF')
    password = forms.CharField(widget=forms.PasswordInput, label='Senha')


    cep = forms.CharField(label='CEP')
    complement = forms.CharField(label='Complemento')
    neighborhood = forms.CharField(label='Bairro')
    street = forms.CharField(label='Logradouro')
    number = forms.CharField(label='Número')
    city = forms.CharField(label='Cidade')
    state = forms.CharField(label='Estado')

    class Meta:
        model = Patient
        fields = ['name', 'telephone', 'username', 
                'cpf', 'password', 'street', 'number', 
                'city', 'state', 'complement', 'neighborhood']


    def save(self, commit=True):
        user = CustomUser.objects.create_user(
            username=self.cleaned_data['username'],
            cpf=self.cleaned_data['cpf'],
            password=self.cleaned_data['password'],
            type='Paciente'
        )

        address = Address.objects.create(
            user=user,
            cep=self.cleaned_data['cep'],
            complement=self.cleaned_data['complement'],
            neighborhood=self.cleaned_data['neighborhood'],
            street=self.cleaned_data['street'],
            number=self.cleaned_data['number'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
        )

        patient = super().save(commit=False)
        patient.user = user
        patient.address = address

        if commit:
            patient.save()
        return patient