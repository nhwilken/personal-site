from RecipeManager.models import *

def runit ():
	for recipe in Recipe.objects.all():
		for version in recipe.versions.all():
			print(version.id)
			for method in version.methods.all():
				print(method.desc)
				if method.desc is not None:
					print(method.desc)
			