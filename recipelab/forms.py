from django import forms
from .models import *


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = ('recipe_name',)
        widgets = {
            'recipe_name': forms.TextInput(
                attrs={'id': 'new-recipe-name',
                       'required': True,
                       'placeholder': 'New recipe name...'}
            ),
        }


class VersionForm(forms.ModelForm):

    class Meta:
        model = Version
        fields = ('recipe',
                  'version_num',
                  'favorite',
                  'date_created',
                  'notes',
                  )


class ItemListForm(forms.ModelForm):

    class Meta:
        model = ItemList
        fields = ('version',
                  'name',
                  'amount',
                  'unit',
                  )
        # widget
        widgets = {
            'amount': forms.TextInput(attrs={'size': '30'}),
        }


# class MethodForm(forms.ModelForm):
#
#     class Meta:
#         model = Method
#         fields = ('version',
#                   'desc',
#                   'order',
#                   )
#         widgets = {
#             'desc': forms.TextInput(attrs={'size': '10'}),
#         }
