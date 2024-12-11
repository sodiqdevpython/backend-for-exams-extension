from django.db import models


class Subject(models.Model):
	key = models.TextField()
	value = models.TextField()

	def __str__(self):
		return str(self.id)

