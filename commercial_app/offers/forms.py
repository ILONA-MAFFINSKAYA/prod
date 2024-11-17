from django import forms
from .models import Offer, OfferProduct, Product

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['executor', 'customer', 'note', 'delivery', 'payment_terms']
        labels = {
            'executor': 'Исполнитель',
            'customer': 'Заказчик',
            'note': 'Примечание',
            'delivery': 'Доставка',
            'payment_terms': 'Условия оплаты',
        }

class OfferProductForm(forms.ModelForm):
    class Meta:
        model = OfferProduct
        fields = ['product', 'quantity']
        labels = {
            'product': 'Продукт',
            'quantity': 'Количество',
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'type', 'tags', 'article']
        labels = {
            'name': 'Название',
            'price': 'Цена',
            'type': 'Тип',
            'tags': 'Теги',
            'article': 'Артикул',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'article': forms.TextInput(attrs={'class': 'form-control'}),
        }