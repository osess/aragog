#coding:utf-8
from django                     import forms

from .models import AdministrativeArea
from .models import Place

class AdministrativeAreaForm(forms.ModelForm):
    class Meta:
        model = AdministrativeArea
        exclude = (
            'description',
            'slug',
            'active',
            'area_property',
            'abolished_date',
        )

class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        exclude = (
            'site',
            'user',
            'owner',
            'category',
            'slug',
            'longitude',
            'latitude',
            'description',
            'added_on',
            'updated_on',
        )
        include = (
            'street',
            'phone',
            'postal_code',
            'is_public',
        )