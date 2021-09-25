from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
# Create your views here.

def analyzer(request):
    template = loader.get_template('data_analyzer/data_analyzer.html')
    context = {}
    response = HttpResponse(template.render(context, request))
    return response


def form_builder(request):
    template = loader.get_template('data_analyzer/build_form.html')
    context = {}
    response = HttpResponse(template.render(context, request))
    return response
