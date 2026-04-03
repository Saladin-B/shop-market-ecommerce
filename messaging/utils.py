import qrcode
from io import BytesIO
import base64
from django.conf import settings


def generate_qr_code(shop_profile_id):
    """Generate a QR code that links to the subscription page"""
    subscription_url = f"{settings.SITE_URL}/subscribe/{shop_profile_id}/"
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


def download_qr_code(shop_profile_id, filename):
    """Generate QR code as downloadable PNG"""
    subscription_url = f"{settings.SITE_URL}/subscribe/{shop_profile_id}/"
    qr = qrcode.QRCode()
    qr.add_data(subscription_url)
    qr.make()
    img = qr.make_image()
    img.save(filename)
    return img
