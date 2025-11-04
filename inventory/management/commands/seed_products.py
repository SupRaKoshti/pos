from django.core.management.base import BaseCommand
from inventory.models import ProductCategory, ProductSubCategory, Product, ProductVariant, InventoryItem
from datetime import date
from decimal import Decimal
import random

class Command(BaseCommand):
    help = "Seed realistic product data with real-world names and variants."

    def handle(self, *args, **options):
        # -------------------------------
        # 1️⃣ Product Categories
        # -------------------------------
        categories = {
            "Electronics": ["Mobile Phones", "Laptops", "Headphones"],
            "Clothing": ["Men's Wear", "Women's Wear", "Kids' Wear"],
            "Food & Beverages": ["Snacks", "Beverages", "Dairy"],
            "Books": ["Fiction", "Education", "Comics"],
            "Sports": ["Fitness", "Outdoor", "Accessories"],
            "Home & Garden": ["Furniture", "Decor", "Kitchen"]
        }

        # -------------------------------
        # 2️⃣ Realistic Product Data
        # -------------------------------
        product_data = {
            "Mobile Phones": ["iPhone 15 Pro", "Samsung Galaxy S24", "OnePlus 12", "Google Pixel 9"],
            "Laptops": ["MacBook Air M3", "Dell XPS 15", "HP Spectre x360", "Lenovo ThinkPad X1"],
            "Headphones": ["Sony WH-1000XM5", "AirPods Pro 2", "Bose QC 45", "JBL Tune 760NC"],
            
            "Men's Wear": ["Levi’s 511 Jeans", "Nike Sports T-Shirt", "Adidas Hoodie", "Puma Jacket"],
            "Women's Wear": ["Zara Summer Dress", "H&M Blazer", "Forever 21 Top", "Levi’s Denim Skirt"],
            "Kids' Wear": ["Carter’s Pajama Set", "H&M Kids Hoodie", "Puma Sneakers", "Gap Kids Jeans"],
            
            "Snacks": ["Lays Classic Chips", "Doritos Nacho Cheese", "Oreo Cookies", "Pringles Original"],
            "Beverages": ["Coca-Cola 1L", "Pepsi 1L", "Tropicana Orange Juice", "Red Bull Energy Drink"],
            "Dairy": ["Amul Butter 500g", "Nestle Milk 1L", "Mother Dairy Curd 400g", "Cheddar Cheese 200g"],
            
            "Fiction": ["The Alchemist", "Harry Potter and the Sorcerer’s Stone", "1984 by George Orwell"],
            "Education": ["Python Programming 101", "Data Science Made Easy", "Mathematics for Engineers"],
            "Comics": ["Spider-Man Vol. 1", "Batman: The Killing Joke", "Avengers: Infinity Saga"],
            
            "Fitness": ["Yoga Mat Pro", "Dumbbell Set 10kg", "Resistance Bands Pack", "Treadmill X2000"],
            "Outdoor": ["Adidas Football", "Yonex Badminton Racket", "Wilson Tennis Ball Set", "Camping Tent 4P"],
            "Accessories": ["Water Bottle Steel", "Gym Gloves", "Smart Fitness Watch", "Sweatband Set"],
            
            "Furniture": ["Wooden Dining Table", "Queen Bed Frame", "Office Chair Ergonomic", "Sofa Set 3-Seater"],
            "Decor": ["Wall Art Canvas", "Table Lamp", "Flower Vase Ceramic", "Decorative Clock"],
            "Kitchen": ["Non-stick Pan", "Pressure Cooker", "Stainless Steel Knife Set", "Blender Pro 500W"],
        }

        # -------------------------------
        # 3️⃣ Create Categories & Subcategories
        # -------------------------------
        category_objs = {}
        subcategory_objs = {}

        for cat_name, subs in categories.items():
            category, _ = ProductCategory.objects.get_or_create(
                name=cat_name,
                defaults={"description": f"All kinds of {cat_name.lower()} products."}
            )
            category_objs[cat_name] = category

            for sub in subs:
                subcat, _ = ProductSubCategory.objects.get_or_create(
                    name=sub,
                    category=category,
                    defaults={"description": f"{sub} under {cat_name} category."}
                )
                subcategory_objs[sub] = subcat

        self.stdout.write(self.style.SUCCESS("✅ Categories and subcategories created."))

        # -------------------------------
        # 4️⃣ Create Products & Variants
        # -------------------------------
        all_products = []
        all_variants = []

        for sub_name, products in product_data.items():
            subcat = subcategory_objs.get(sub_name)
            for product_name in products:
                product, _ = Product.objects.get_or_create(
                    name=product_name,
                    subcategory=subcat,
                    defaults={"description": f"High quality {product_name} available in store."}
                )
                all_products.append(product)

                # Create realistic variants
                variant_names = [
                    "Standard Edition", "Pro Edition", "Limited Edition"
                ]
                for v_name in variant_names[: random.randint(1, 3)]:
                    price = Decimal(random.uniform(500, 20000)).quantize(Decimal("0.00"))
                    sku = f"SKU-{product.id}-{v_name[:3].upper()}-{random.randint(1000,9999)}"
                    variant, _ = ProductVariant.objects.get_or_create(
                        product=product,
                        variant_name=v_name,
                        sku=sku,
                        defaults={"price": price}
                    )
                    all_variants.append(variant)

        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(all_products)} products and {len(all_variants)} variants."))

        # -------------------------------
        # 5️⃣ Inventory
        # -------------------------------
        for variant in all_variants:
            InventoryItem.objects.get_or_create(
                item_code=f"INV-{variant.sku}",
                variant=variant,
                defaults={
                    "quantity_in_stock": random.randint(10, 200),
                    "expired_date": date(2026, 12, 31),
                    "batch_number": f"BATCH-{variant.id}"
                }
            )

        self.stdout.write(self.style.SUCCESS("🎉 Realistic sample data seeded successfully!"))
