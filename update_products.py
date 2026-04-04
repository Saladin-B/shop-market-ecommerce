#!/usr/bin/env python
"""
Update products with image files
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')
django.setup()

from payments.models import Product
from django.core.files.base import ContentFile
from pathlib import Path

# Get all products
products = Product.objects.all()
print(f"Found {products.count()} products")

# Read the sample image
image_path = Path('media/products/sample.jpg')
if image_path.exists():
    print(f"Sample image found at {image_path}")
    
    # Update each product with the image
    for product in products:
        if not product.image:
            with open(image_path, 'rb') as f:
                product.image.save('sample.jpg', ContentFile(f.read()), save=True)
            print(f"Updated {product.name} with image")
        else:
            print(f"{product.name} already has image: {product.image}")
else:
    print(f"Sample image not found at {image_path}")
