import os
import django
from project_template.models import Docs

def docs_init():
	root_path = "../docs"
	for root, dirs, files in os.walk(root_path):
		for f in files:
			c = Chunks(address = root+f)
			c.save()

docs_init()