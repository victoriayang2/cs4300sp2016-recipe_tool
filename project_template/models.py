from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Combined(models.Model):
	id = models.IntegerField(primary_key=True)  # AutoField?
	recipe = models.IntegerField(db_column='recipe', unique=True)  # Field name made lowercase.
	scores = models.BinaryField(db_column='scores')  # Field name made lowercase.
	class Meta:
		managed = False
		db_table = 'combined'

class Metadata(models.Model):
	id = models.IntegerField(primary_key=True)  # AutoField?
	ratings = models.BinaryField(blank=True, null=True)
	times = models.BinaryField(blank=True, null=True)
	class Meta:
		managed = False
		db_table = 'metadata'