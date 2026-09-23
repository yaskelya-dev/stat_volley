from django.shortcuts import render


def home_view(request):
    context = {
        'page_title': 'Главная страница статистики',
    }
    return render(request, 'home/home.html', context)
