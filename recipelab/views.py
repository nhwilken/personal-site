from django.shortcuts import render, redirect, get_object_or_404
from .forms import RecipeForm
from django import forms
from .models import Recipe, Version, ItemList
from django.forms import inlineformset_factory
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
import re
from django.utils import formats
import json


def recipe_list(request):
    """
    Retrieves a list of recipes from the database
    shows a simple list of all the recipes in the database
    """

    recipelist = Recipe.objects.all().order_by('recipe_name')
    new_recipe_form = RecipeForm()

    context = {
        'recipe_list': recipelist,
        'recipe_form': new_recipe_form,
    }

    return render(request, 'recipemanager/recipe_list.html', context)


def recipe_detail(request, pk):
    """
    A detailed view of the selected recipe in recipe_id from index
    """

    # recipe = Recipe.objects.get(pk=pk)
    recipe = get_object_or_404(Recipe, pk=pk)
    versions = list(recipe.versions.all().order_by('-date_created'))
    current_version = versions[0]
    print("Current version: " + str(current_version.id))
    context = {
        'recipe': recipe,
        'current_version': current_version,
        'versions': versions,
        'method_list': current_version.method_as_list(),
    }

    return render(request, 'recipemanager/recipe_detail.html', context)


def recipe_new(request):
    """
    Creates a new recipe with an empty version

    """
    if request.method == 'POST':
        print('the form was submmited')

        new_name = request.POST.get('recipe_name')

        recipe = Recipe(recipe_name=new_name)
        recipe.save()
        first_version = Version(recipe=recipe)
        first_version.save()
        recipe_html_rendered = render_to_string('recipemanager/recipe_list_item.html', {'recipe': recipe})

        response = {
            'recipe_name': recipe.recipe_name,
            'recipe_id': recipe.id,
            'recipe_html': recipe_html_rendered,
        }

        return JsonResponse(response)
    else:
        return JsonResponse({})


def add_version(request, recipe_id):
    """
    Create a new version for  recipe from the recipe detail view screen
    :param request:
    :param recipe_id: the id of the recipe
    :return: redirect to reload recipe_detail
    """
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    # get the latest version number from the model
    version_num = recipe.latest_version()
    # create a new version
    Version.objects.create(recipe=recipe,
                           version_num=version_num+1)

    # reload recipe_detail
    return redirect('recipe_detail', pk=recipe_id)


def delete_version(request, version_id):

    version = get_object_or_404(Version, pk=version_id)
    recipe_id = version.recipe.id

    version.delete()

    return redirect('recipe_detail', pk=recipe_id)


def recipe_edit(request, pk, version_num):

    ItemListFormSet = inlineformset_factory(Version, ItemList, extra=0,
                fields=('amount', 'unit', 'name',),
                widgets={'amount': forms.TextInput(attrs={
                                                    'size': '2',
                                                    'class': 'form-control'}),
                         'unit': forms.Select(attrs={
                                                    # 'size': '3',
                                                    'class': 'form-control'}),
                         'name': forms.TextInput(attrs={
                                                    'class': 'form-control'}),
                         })

    MethodFormSet = inlineformset_factory(Version, Method, extra=0,
                fields=('desc',),
                widgets={'desc': forms.Textarea(attrs={
                                                    'rows': 2,
                                                    'cols': 20,
                                                    'class': 'form-control',
                                                    })})

    recipe = Recipe.objects.get(pk=pk)
    version = recipe.versions.get(version_num=version_num)

    if request.method == 'POST':
        itemformset = ItemListFormSet(request.POST,
                                      request.FILES,
                                      instance=version)

        methodformset = MethodFormSet(request.POST,
                                      request.FILES,
                                      instance=version)

        if itemformset.is_valid() and methodformset.is_valid():
            itemformset.save()
            methodformset.save()
            return redirect('recipe_detail', pk=pk)

    itemformset = ItemListFormSet(instance=version)
    methodformset = MethodFormSet(instance=version)

    context = {
        'pk': pk,
        'recipe': recipe,
        'version': version,
        'version_id': version.id,
        'itemform': itemformset,
        'methodform': methodformset,
    }

    return render(request,
                  'recipemanager/recipe_edit.html',
                  context)


def search_recipe_list(request):

    if request.method == "GET":

        srch_term = request.GET.get('srch_term')
        return_type = request.GET.get('return_type')


        # return types: list, json/dict, html
        if srch_term != "":
            recipes = Recipe.objects.filter(recipe_name__icontains=srch_term)
        else:
            recipes = Recipe.objects.all()

        if return_type == 'html':
            # if html is wanted, need to build from the template
            as_html = ''
            for recipe in recipes:
                as_html += render_to_string('recipemanager/recipe_list_item.html', {'recipe': recipe})
                as_html += '\n'

            return JsonResponse({'html': as_html})

        if return_type == 'list':
            as_list = recipes.values_list('recipe_name', flat=True)

            return JsonResponse({'list': as_list})


def list_to_form(request, recipe_id):
    """
    handles ajax request for recipe edits
    On GET request - return combine item and method data as on string
    On POST - split return item and method strings into lists - save to DB
    :param request: 
    :param recipe_id: 
    :return: 
    """

    if request.method == 'GET':
        version_id = request.GET.get('version')
        version = get_object_or_404(Version, pk=version_id)

        context = {
            'current_version': version,
            'item_text': version.items_as_text(),
            'method_text': version.method,
            'method_list': version.method_as_list()
                   }

        if request.GET.get('return_type') == "plain":
            html = render_to_string('recipemanager/recipe_display.html',
                                    context)
        else:
            html = render_to_string('recipemanager/recipe_display_asform.html',
                                    context)

        response = {
            'new_display': html,
        }

        return JsonResponse(response)

    elif request.method == "POST":
        print('it was a post')
        version_id = request.POST.get('version')
        version = get_object_or_404(Version, pk=version_id)
        # get the data from the post
        item_text = request.POST.get('item_data')
        method_text = request.POST.get('method_data')
        # extract the items from the item text
        newitem_dict = split_item_list(item_text)

        if request.POST.get('save_type') == 'revise':
            print('type is revise')
            # compare the new recipe with the old recipe, to see what changed
            olditem_dict = version.items_as_dict()
            added, removed, edited = compare_dict(olditem_dict, newitem_dict)

            for item in added:
                # create new item in the existing version
                # version name amount unit
                temp_item = ItemList(version=version,
                                     name=item,
                                     amount=added[item][0],
                                     unit=added[item][1])
                temp_item.save()
            for item in removed:
                # remove item from existing version
                version.items.get(name=item).delete()
            for item in edited:
                # change item in existing version with revision
                temp_item = version.items.get(name=item)
                temp_item.amount = edited[item][0]
                temp_item.unit = edited[item][1]
                temp_item.save()

            # save the method in the version
            version.method = request.POST.get('method_data')
            version.notes = request.POST.get('general_note')
            version.change_note = request.POST.get('change_note')
            version.result_note = request.POST.get('result_note')
            version.save()

            context = {
                'current_version': version,
                'method_list': version.method_as_list(),
            }

            html = render_to_string('recipemanager/recipe_display.html',
                                    context,)

            response = {
                'new_display': html
            }
            return JsonResponse(response)

        elif request.POST.get('save_type') == 'as-new-version':
            print('Creating a new version')
            recipe = Recipe.objects.get(id=recipe_id)
            new_version = Version(recipe=recipe,
                                  version_num=recipe.latest_version()+1,
                                  method=method_text,
                                  )
            new_version.save()

            items = []
            for name in newitem_dict:

                item = ItemList(version=new_version,
                                name=name,
                                amount=newitem_dict[name][0],
                                unit=newitem_dict[name][1],
                                )
                items.append(item)

            ItemList.objects.bulk_create(items)

            # Prepare the reply
            context = {
                'current_version': new_version,
                'item_text': new_version.items_as_text(),
                'method_text': new_version.method,
            }

            html = render_to_string('recipemanager/recipe_display_asform.html',
                                    context)
            date_created = new_version.date_created
            date_created = formats.date_format(date_created,
                                               "SHORT_DATETIME_FORMAT")
            print(date_created)
            response = {
                'new_display': html,
                'version_id': new_version.id,
                'version_num': new_version.version_num,
                'date_created': date_created,

            }
            return JsonResponse(response)


def split_item_list(item_list):
    """
    Takes a string containing item list information, splits the items and
    returns a dictionary with the item list with item names as keys
    :param item_list: string with item info
    :return: dictionary in the form {'item name': [amount, unit],}
    """

    units = ['\b(?i)cup(s)?\b', '\bml\b', '\bg\b', '\bkg\b', '\bl\b', ]
    unit_regex = "(" + ")|(".join(units) + ")"

    numbers = ['[0-9]+(.[0-9]+)?']
    quantity_regex = "(" + ")|(".join(numbers) + ")"

    split_list = {}
    for line in item_list.splitlines():
        words = line.split()
        unit = None
        quantity = None
        desc = []
        print(words)
        for word in words:
            print(word)
            if re.match(unit_regex, word):
                unit = word
            elif re.match(quantity_regex, word):
                quantity = word
            else:
                desc.append(word)

        if type(quantity) is None:
            quantity = 0

        split_list[" ".join(desc)] = [float(quantity), unit]

    return split_list


def compare_dict(base_dict, new_dict):
    """
    Compares two dictionaries to detect changes between the base dictionary and
    the changed dictionary. Returns three dictionaries: add, remove, edit which
    contains keys that were adding in new dictionary, keys that were removed 
    from the original, and keys that exist in both dictionaries but with changed 
    values.
    :param base_dict: a dictionary with the original key values pairs
    :param new_dict: a dictionary with changed key value pairs
    :return: three dictionaries: added, removed, edited
    """
    added = {}
    removed = {}
    edited = {}

    for key in new_dict:
        # check if the new key exists in the base dict
        if key in base_dict:
            # mark as edited if it is changed, otherwise ignore
            if new_dict[key] != base_dict[key]:
                edited[key] = new_dict[key]
            # remove the key from the base dictionary to mark it as dealt with
            del base_dict[key]
        else:
            # key is not in base_dict, so its a new item
            added[key] = new_dict[key]

    for key in base_dict:
        # all the keys remaining in base_dict were not in new_dict, so they
        # removed in the new list
        removed[key] = base_dict[key]

    return added, removed, edited

