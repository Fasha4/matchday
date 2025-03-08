from django.db import models

# Create your models here.
class Name(models.Model):
	name_matchday = models.CharField(max_length=255)
	name_onefootball = models.CharField(max_length=255, blank=True)
	name_fifa = models.CharField(max_length=255, blank=True)
	name_viaplay = models.CharField(max_length=255, blank=True)
	name_apple = models.CharField(max_length=255, blank=True)
	name_polsat = models.CharField(max_length=255, blank=True)

	def __str__(self):
		return f"{self.name_matchday}"

class Image(models.Model):
	url = models.CharField(max_length=255)
	width = models.IntegerField()
	height = models.IntegerField()

	def __str__(self):
		return f"{self.url}"

class Sport(models.Model):
	name = models.CharField(max_length=255)

	def __str__(self):
		return f"{self.name}"

class League(models.Model):
	name = models.OneToOneField(Name, on_delete=models.PROTECT)
	sport = models.ForeignKey(Sport, on_delete=models.PROTECT)
	image = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, blank=True)
	language = models.CharField(max_length=255, blank=True)

	def __str__(self):
		return f"{self.name}"

class Team(models.Model):
	name = models.OneToOneField(Name, on_delete=models.PROTECT)
	sport = models.ForeignKey(Sport, on_delete=models.PROTECT)
	leagues = models.ManyToManyField(League)

	def __str__(self):
		return f"{self.name}"

class Match(models.Model):
	sport = models.ForeignKey(Sport, on_delete=models.PROTECT)
	league = models.ForeignKey(League, on_delete=models.PROTECT)
	home = models.ForeignKey(Team, on_delete=models.PROTECT, blank=True, related_name="%(class)s_home")
	away = models.ForeignKey(Team, on_delete=models.PROTECT, blank=True, related_name="%(class)s_away")
	event_name = models.CharField(max_length=255, blank=True, help_text="Jeżeli nie wybrano wyżej dwóch drużyn")
	time = models.DateTimeField()
	note = models.CharField(max_length=255, blank=True)

	def __str__(self):
		return f"{self.home} - {self.away}"

class Channel_Type(models.Model):
	name = models.CharField(max_length=255)

	def __str__(self):
		return f"{self.name}"

class Channel(models.Model):
	name = models.CharField(max_length=255)
	type = models.ForeignKey(Channel_Type, on_delete=models.CASCADE)

	def __str__(self):
		return f"{self.name}"

class Commentator(models.Model):
	name = models.CharField(max_length=255)

	def __str__(self):
		return f"{self.name}"

class Broadcast(models.Model):
	match = models.ForeignKey(Match, on_delete=models.PROTECT)
	channel = models.ForeignKey(Channel, on_delete=models.PROTECT)
	commentators = models.ManyToManyField(Commentator)

	def __str__(self):
		return f"{self.match}"
