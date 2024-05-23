from django.shortcuts import render
from positionfinder.views_helpers import get_menu_options


def about_view(request):
    menu_options = get_menu_options() 
    context = {
        'show_fretboard': False,
    }
    context.update(menu_options)
    return render(request, 'about.html', context)
