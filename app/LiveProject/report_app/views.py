from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from .forms import playerForm, leagueForm

from django.http import HttpResponseRedirect
from django.urls import reverse


# from app.src.paths import REPORT_DIR,WEEKLY_REPORT_DIR
from report import LeagueWeeklyReport


# Create your views here.
def home(request):
    return render(request, "base.html")


class reportView(TemplateView):
    template_name = "report.txt"

    def get_context_data(self, **kwargs):  # compartmentalize and build better frontend
        context = super().get_context_data()

        # first check redis cache
        obj = LeagueWeeklyReport(self.kwargs["gid"], self.kwargs["id"])
        obj.weekly_score_transformation()
        obj.merge_league_weekly_transfer()
        obj.add_auto_sub()
        context = obj.create_report()
        # write to cache
        return context


class PlayerReport(FormView):
    form_class = playerForm
    template_name = "player_form.html"

    def get_success_url(self):
        pass

    def form_valid(self, form):
        return super().form_valid(form)


class LeagueReport(FormView):
    form_class = leagueForm
    template_name = "league_form.html"

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
            id = form.cleaned_data["league_id"]
            gid = form.cleaned_data["gameweek"]
            print(id)
            return HttpResponseRedirect(reverse("report", args=[id, gid]))
    else:
        form = leagueForm()

    return render(request, "league_form.html", {"form": form})
