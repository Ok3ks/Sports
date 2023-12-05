from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from .forms import playerForm, leagueForm

from django.http import HttpResponseRedirect
from django.urls import reverse

import json
#from app.src.paths import REPORT_DIR,WEEKLY_REPORT_DIR
from os.path import realpath, join

# Create your views here.
def home(request):
    return render(request, 'base.html')

class reportView(TemplateView):
    template_name = "report.txt"
    def get_context_data(self, **kwargs): #compartmentalize and build better fronted
        #file = realpath(join(WEEKLY_REPORT_DIR, '{}_{}.json'.format(self.league_id, self.gw)))
        
        file = "/Users/max/Desktop/Sports/app/LiveProject/templates/{}.json".format(self.kwargs['id'])

        #S3 each league per bucket
        #upon submission, redirect to your api for analysis 
        #then render output later
        #When they sign up, more db space, more eager loading.
        #Fplwrap as email, 

        context = super().get_context_data()
        print(context)
        with open (file, 'r') as ins:
            context = json.load(ins)
        return context
    
class PlayerReport(FormView):
    form_class = playerForm
    template_name = 'player_form.html'

    def get_success_url(self):
        pass

    def form_valid(self, form):
        return super().form_valid(form)

class LeagueReport(FormView):
    form_class = leagueForm
    template_name = 'league_form.html'

    def get_success_url(self):
        pass

    def form_valid(self, form):
        return super().form_valid(form)


def display(request):
    if request.method == "POST":
        form = leagueForm(request.POST)
        if form.is_valid():
            # Do something with the form data
            # like send an email.
            # createreport and save json in templates
            id = form.cleaned_data['league_id']
            print(id)
            return HttpResponseRedirect(
                reverse('report', args=[id]))
    else:
        form = leagueForm()

    return render(
        request,
        'league_form.html',
        {'form': form}
    )