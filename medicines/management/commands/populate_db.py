from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from medicines.models import Category, Medicine
from users.models import User
import os
import random

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        # Create categories
        categories = ['Pain Relief', 'Wellness', 'Cardiac', 'Neurology', 'Dermatology']
        for cat_name in categories:
            Category.objects.get_or_create(name=cat_name)
        self.stdout.write(self.style.SUCCESS('Categories created'))

        # Get or create a distributor
        distributor, created = User.objects.get_or_create(
            username='vertex_pharma',
            email='sales@vertex.com',
            role='distributor'
        )
        if created:
            distributor.set_password('distributor123')
            distributor.company_name = 'Vertex Pharmaceuticals'
            distributor.gst_number = '29ABCDE1234F1Z5'
            distributor.drug_license = 'KA-BLR-123456'
            distributor.save()

        # Sample Medicines
        medicines = [
            {
                'name': 'Wellness Plus',
                'category': 'Wellness',
                'price': 599,
                'stock': 100,
                'description': 'Premium multivitamin capsules formulated for optimal daily nutrition. Boost your immunity and energy naturally.',
                'image_src': 'product-neurozen.png',
                'prescription': False
            },
            {
                'name': 'Calm Serum',
                'category': 'Neurology',
                'price': 449,
                'stock': 50,
                'description': 'Natural lavender-infused wellness serum for relaxation and peaceful sleep. Doctor recommended for stress management.',
                'image_src': 'product-calmia.png',
                'prescription': False
            },
            {
                'name': 'Regenerate',
                'category': 'Wellness',
                'price': 799,
                'stock': 75,
                'description': 'Advanced supplement blend for cellular health and vitality. Perfect for post-workout recovery and anti-aging.',
                'image_src': 'product-regenrx.png',
                'prescription': False
            },
            {
                'name': 'NeuroPain X',
                'category': 'Pain Relief',
                'price': 120,
                'stock': 200,
                'description': 'Fast acting pain relief gel for joint and muscle pain. Contains Diclofenac and Menthol.',
                'image_src': None,
                'prescription': True
            },
            {
                'name': 'CardioGuard',
                'category': 'Cardiac',
                'price': 85,
                'stock': 500,
                'description': 'Beta-blocker for hypertension and angina. Requires valid prescription.',
                'image_src': None,
                'prescription': True
            }
        ]

        for med in medicines:
            cat = Category.objects.get(name=med['category'])
            obj, created = Medicine.objects.get_or_create(
                name=med['name'],
                defaults={
                    'category': cat,
                    'price': med['price'],
                    'mrp': int(med['price'] * 1.2),
                    'stock': med['stock'],
                    'description': med['description'],
                    'distributor': distributor,
                    'requires_prescription': med['prescription'],
                    'manufacturer': 'NeuroVaidya Labs',
                    'pack_size': '30 Units'
                }
            )
            
            # Copy image if exists and not already set
            if med['image_src'] and created:
                src_path = os.path.join(os.getcwd(), 'static', 'images', med['image_src'])
                if os.path.exists(src_path):
                    with open(src_path, 'rb') as f:
                        obj.image.save(med['image_src'], ContentFile(f.read()), save=True)

        self.stdout.write(self.style.SUCCESS(f'Successfully populated {len(medicines)} medicines'))
