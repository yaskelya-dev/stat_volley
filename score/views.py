from django.shortcuts import render
from users.decorators import login_required_message

@login_required_message(redirect_after_login='score:index')
def index(request):
    return render(request, 'score/index.html')
