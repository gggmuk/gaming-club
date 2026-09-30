import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crm_core.models import Place, Tariff

print("=== Checking Places and Tariffs ===\n")

places = Place.objects.all()
for p in places:
    if p.tariff:
        print(f"{p.name}: {p.tariff.name} - {p.tariff.hourly_rate}₽/ч")
    else:
        print(f"{p.name}: NO TARIFF ASSIGNED!")

print("\n=== All Tariffs ===\n")
tariffs = Tariff.objects.all()
for t in tariffs:
    print(f"{t.name}: {t.hourly_rate}₽/ч (Active: {t.is_active})")
