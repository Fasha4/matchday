from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Team, Name
from .forms import SportForm

def matches(request):

	if request.method == "POST":
		form = SportForm()
		if form.is_valid():
			print("ok")

	else:
		form = SportForm()

	context = {
	'form': form
	}
	return render(request, 'add_matches.html', context)