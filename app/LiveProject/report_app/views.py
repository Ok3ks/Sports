from django.shortcuts import render
from django.views.generic.base import TemplateView

import json
from app.src.paths import REPORT_DIR
from os.path import realpath

# Create your views here.
def home(request):
    return render(request, 'base.html')

class reportView(TemplateView):
    template_name = "report.txt"

    def get_context_data(self, file = '/Users/max/Desktop/Sports/app/LiveProject/templates/85647_13.json'): #compartmentalize and build better fronted
        context = super().get_context_data()
        with open (file, 'r') as ins:
            context = json.load(ins)
        return context