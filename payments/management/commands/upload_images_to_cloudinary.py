from django.core.management.base import BaseCommand
from django.conf import settings
from payments.models import Product
from decouple import config
import cloudinary
import cloudinary.uploader
import os


class Command(BaseCommand):
    help = 'Upload local product images to Cloudinary'

    def handle(self, *args, **options):
        # Configure cloudinary
        cloudinary.config(
            cloud_name=config("CLOUDINARY_CLOUD_NAME"),
            api_key=config("CLOUDINARY_API_KEY"),
            api_secret=config("CLOUDINARY_API_SECRET"),
        )

        products = Product.objects.exclude(image='')
        total = products.count()
        self.stdout.write(f"Found {total} products with images to upload")

        uploaded = 0
        errors = []

        for product in products:
            try:
                # Get the file path
                file_path = product.image.path
                
                # Skip if file doesn't exist
                if not os.path.exists(file_path):
                    self.stdout.write(self.style.WARNING(f"[WARNING] File not found: {file_path}"))
                    errors.append(f"{product.name}: File not found")
                    continue

                # Construct public_id to maintain folder structure
                public_id = str(product.image).replace('\\', '/')  # e.g., "products/filename.jpg"
                public_id = public_id.rsplit('.', 1)[0]  # Remove extension

                # Upload to Cloudinary
                result = cloudinary.uploader.upload(
                    file_path,
                    public_id=public_id,
                    overwrite=True,
                    resource_type='auto'
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"[SUCCESS] Uploaded: {product.name} ({product.id})"
                    )
                )
                uploaded += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"[ERROR] Error uploading {product.name}: {str(e)}"
                    )
                )
                errors.append(f"{product.name}: {str(e)}")

        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"[SUCCESS] Successfully uploaded: {uploaded}/{total}"))
        if errors:
            self.stdout.write(self.style.ERROR(f"[ERROR] Errors ({len(errors)}):"))
            for error in errors:
                self.stdout.write(f"  - {error}")
        self.stdout.write("="*50)
