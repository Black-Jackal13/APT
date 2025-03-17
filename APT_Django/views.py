from django.http import HttpResponse
from django.template import loader


# Create your views here.
def index(request):
    page = loader.get_template("index.html")
    return HttpResponse(page.render())


def races(request):
    page = loader.get_template("races.html")
    races_data = Race.objects.all()
    return HttpResponse(page.render({"races": races_data}))


def available_predictions(request):
    page = loader.get_template("predictions.html")
    return HttpResponse(page.render())


def current_results(request):
    page = loader.get_template("results.html")
    return HttpResponse(page.render())
