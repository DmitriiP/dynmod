import subprocess
import time
# import dynmod.models
from dynmod.models import model_factory
from django.http import HttpResponse
from django.core.management import call_command
from django.shortcuts import redirect, render_to_response
from django.core.context_processors import csrf

def home(request):
    call_command('makemigrations', 'dynmod', interactive=False)
    call_command('migrate', interactive=False)
    return render_to_response('home.html')

def restart(request):
    subprocess.call(['touch', 'dynmod/views.py'])
    return redirect('/')

def models_editor(request):
    if request.method == "POST":
        f = open('dynmod/models.json', 'r')
        old = f.read()
        f.close()
        new = request.POST.get('models', old)
        f = open('dynmod/models.json', 'w')
        f.write(new)
        f.close
        return redirect('/restart/')

    f = open('dynmod/models.json', 'r')
    context = {
        'models': f.read()
    }
    context.update(csrf(request))
    return render_to_response('models_editor.html', context)
