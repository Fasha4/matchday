from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Team, Name

def matches(request):
	teams = Name.objects.all().values()
	template = loader.get_template('add_matches.html')
	context = {
	'teams': teams,
	}
	return HttpResponse(template.render(context, request))