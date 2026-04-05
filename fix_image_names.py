"""Fix product image filename in database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')
django.setup()

from payments.models import Product

# Fix the Sensation product with mismatched filename
p = Product.objects.get(name="Sensation")
print(f"Before: {p.image.name}")
p.image.name = "products/omar-al-ghosson-Q_TaBnDxqd0-unsplash.jpg"
p.save()
print(f"After: {p.image.name}")
