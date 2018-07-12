from django.forms import ModelForm

from .models import Checkout


class CheckoutCreateForm(ModelForm):

    class Meta:
        model = Checkout
        fields = [] #fields = ['project', 'editor']
