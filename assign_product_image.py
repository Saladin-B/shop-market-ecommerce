#!/usr/bin/env python
"""
Assign images to products that don't have them
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')
django.setup()

from payments.models import Product
from django.core.files.base import ContentFile
from pathlib import Path

# Get all products without images
products_without_images = Product.objects.filter(image__isnull=True) | Product.objects.filter(image__exact='')

print(f"Found {products_without_images.count()} products without images")

# Read sample image
image_path = Path('media/products/sample.jpg')
if image_path.exists():
    print(f"Sample image found at {image_path}")
    
    # Update each product with the image
    for product in products_without_images:
        try:
            with open(image_path, 'rb') as f:
                product.image.save('sample.jpg', ContentFile(f.read()), save=True)
            print(f"✓ Updated '{product.name}' with image")
        except Exception as e:
            print(f"✗ Failed to update '{product.name}': {str(e)}")
else:
    print(f"Sample image not found at {image_path}")
    # Try alternative image
    alt_image_path = Path('media/products/pexels-vldsx-500651237-30618765.jpg')
    if alt_image_path.exists():
        print(f"Found alternative image: {alt_image_path.name}")
        for product in products_without_images:
            try:
                with open(alt_image_path, 'rb') as f:
                    product.image.save(alt_image_path.name, ContentFile(f.read()), save=True)
                print(f"✓ Updated '{product.name}' with alternative image")
            except Exception as e:
                print(f"✗ Failed to update '{product.name}': {str(e)}")
    else:
        print("No suitable image found")

# Verify
print("\nVerification:")
all_products = Product.objects.all()
for product in all_products:
    has_img = "✓ Has image" if product.image else "✗ No image"
    print(f"  {product.name}: {has_img}")
