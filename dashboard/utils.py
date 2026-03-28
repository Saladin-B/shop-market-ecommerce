import qrcode
import io
import base64
from django.conf import settings


def generate_qr_code(shop_slug):
    """
    Generate a QR code for the shop's subscription page.
    Returns a base64-encoded PNG image.
    """
    subscription_url = f"{settings.SITE_URL}/subscribe/{shop_slug}/"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(subscription_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return qr_base64, subscription_url