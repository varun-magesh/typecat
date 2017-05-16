from django.shortcuts import render
from django.http import HttpResponse
from fonts.models import FontName
# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def name(request):
    n = 2
    f = FontName.objects.get(id=n)
    return HttpResponse("{},{},{}".format(f.filename, f.name, n))

def img(request):
    f = request.GET["filename"]
    try:
        with open("image-stuff/imgs/{}.jpg".format(f[f.rfind("/"):-4]), "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except IOError:
        #some kind of error handling here
        return HttpResponse("../image-stuff/imgs/{}.jpg".format(f[f.rfind("/")+1:-5]))

def submit(request):
    n = request.POST["id"]
    FontName.objects.get(id=n).add_classification(request.POST["classification"])
    FontName.objects.get(id=n).save()
