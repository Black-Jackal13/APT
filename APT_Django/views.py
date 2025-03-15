from django.http import HttpResponse
from django.template import loader


# Create your views here.
def index(request):
    page = loader.get_template("index.html")
    return HttpResponse(page.render())


def races(request):
    page = loader.get_template("races.html")
    return HttpResponse(page.render())


def available_predictions(request):
    page = loader.get_template("predictions.html")
    return HttpResponse(page.render())


def current_results(request):
    page = loader.get_template("results.html")
    return HttpResponse(page.render())
