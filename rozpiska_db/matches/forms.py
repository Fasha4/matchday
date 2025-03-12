from django import forms

class SportForm(forms.Form):
	name = forms.CharField(label="Nazwa Sportu", max_length=255)