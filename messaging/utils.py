import qrcode
from io import BytesIO
import base64
from django.conf import settings


def generate_qr_code(shop_slug, request=None):
    """Generate a QR code that links to the subscription page"""
    if request:
        # Build URL from request (handles any domain)
        subscription_url = request.build_absolute_uri(f'/messaging/subscribe/{shop_slug}/')
    else:
        # Fallback to settings
        subscription_url = f"{settings.SITE_URL}/messaging/subscribe/{shop_slug}/"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(subscription_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for display
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def download_qr_code(shop_slug, filename):
    """Generate QR code as downloadable PNG"""
    subscription_url = f"{settings.SITE_URL}/messaging/subscribe/{shop_slug}/"
    qr = qrcode.QRCode()
    qr.add_data(subscription_url)
    qr.make()
    img = qr.make_image()
    img.save(filename)
    return img
