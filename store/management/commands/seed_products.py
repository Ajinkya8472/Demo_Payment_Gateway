from django.core.management.base import BaseCommand

from store.models import Product

PRODUCTS = [
    ('Title Card Pack', 'Twelve animated title cards for video intros', 'Twelve editable title cards for Premiere and After Effects. Clean typography, three colour variants each, drop-in ready.', 49900, '#3A5BFF'),
    ('Lower Thirds Kit', 'Name and caption bars that slide in smoothly', 'Eight lower-third animations with adjustable colours and timing. Works with interviews, vlogs and documentaries.', 29900, '#E4572E'),
    ('Social Reel Templates', 'Vertical templates for Reels and Shorts', 'Ten 9:16 reel templates with placeholder slots for your clips, captions and music beats.', 39900, '#1B998B'),
    ('Logo Sting Bundle', 'Short logo reveals under five seconds', 'Six logo reveal animations. Swap in your logo, pick a colour, export.', 24900, '#F2A900'),
]


class Command(BaseCommand):
    help = 'Create demo products (safe to run repeatedly).'

    def handle(self, *args, **options):
        for name, tagline, description, price, color in PRODUCTS:
            _, created = Product.objects.get_or_create(
                name=name,
                defaults=dict(tagline=tagline, description=description, price_paise=price, accent_color=color),
            )
            self.stdout.write(f"{'Created' if created else 'Exists'}: {name}")