from django.shortcuts import render, redirect, get_object_or_404
# from .forms import RecipeForm
from django import forms
# from .models import Recipe, Version, ItemList, Method
from django.forms import inlineformset_factory

# Create your views here.


def main_page(request):
    """
    Return the main page view
    """

    return render(request, 'journal/homesplash.html')