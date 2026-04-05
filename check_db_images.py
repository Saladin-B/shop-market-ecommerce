"""Check product images in database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')
django.setup()

from payments.models import Product

products = Product.objects.filter(image__isnull=False)
for p in products:
    print(f"{p.name}: {p.image.name}")
