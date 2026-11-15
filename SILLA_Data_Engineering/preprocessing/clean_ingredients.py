"""
preprocessing/clean_ingredients.py
=====================================
Builds the canonical ingredients master catalog and cleans recipe ingredients:
1. data/processed/ingredients_master.csv
2. data/processed/recipe_ingredients_clean.csv

Features:
- Bilingual English/Arabic canonical names and aliases
- Dietary tags (vegan, vegetarian, gluten-free, halal, dairy-free)
- Normalized units (mass, volume, count) using normalize_units.py
- Preserves original ingredient text for NLP teams
"""

import logging
import re
from pathlib import Path
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import RAW_DIR, PROCESSED_DIR
from preprocessing.normalize_arabic import normalize_arabic_text
from preprocessing.normalize_units import normalize_unit, normalize_quantity

logger = logging.getLogger(__name__)

RAW_ING_PATH = RAW_DIR / "recipe_ingredients_raw.csv"
MASTER_OUT_PATH = PROCESSED_DIR / "ingredients_master.csv"
CLEAN_RECIPE_ING_PATH = PROCESSED_DIR / "recipe_ingredients_clean.csv"

# Comprehensive dictionary for canonical English & Arabic ingredient mappings
KNOWN_INGREDIENTS = {
    "penne pasta": {"ar": "مكرونة فرن", "category": "Pasta and Grains", "unit": "g", "dietary": "vegan,halal"},
    "spaghetti pasta": {"ar": "مكرونة سباجيتي", "category": "Pasta and Grains", "unit": "g", "dietary": "vegan,halal"},
    "elbow macaroni": {"ar": "مكرونة مقصوصة", "category": "Pasta and Grains", "unit": "g", "dietary": "vegan,halal"},
    "fettuccine pasta": {"ar": "مكرونة فيتوتشيني", "category": "Pasta and Grains", "unit": "g", "dietary": "vegetarian,halal"},
    "lasagna pasta sheets": {"ar": "شرائح لازانيا", "category": "Pasta and Grains", "unit": "g", "dietary": "vegetarian,halal"},
    "vermicelli": {"ar": "شعرية", "category": "Pasta and Grains", "unit": "g", "dietary": "vegan,halal"},
    "egyptian white rice": {"ar": "أرز مصري", "category": "Pasta and Grains", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "basmati rice": {"ar": "أرز بسمتي", "category": "Pasta and Grains", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "brown lentils": {"ar": "عدس بني", "category": "Legumes and Pulses", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "red split lentils": {"ar": "عدس أصفر", "category": "Legumes and Pulses", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "canned chickpeas": {"ar": "حمص معلب", "category": "Legumes and Pulses", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "canned fava beans": {"ar": "فول مدمس معلب", "category": "Legumes and Pulses", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "dried split fava beans": {"ar": "فول مدشوش", "category": "Legumes and Pulses", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "white beans": {"ar": "فاصوليا بيضاء", "category": "Legumes and Pulses", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "chickpeas": {"ar": "حمص", "category": "Legumes and Pulses", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "whole chicken": {"ar": "دجاجة كاملة", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "chicken breast": {"ar": "صدور دجاج", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "chicken thighs": {"ar": "أوراك دجاج", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "ground beef": {"ar": "لحم بقري مفروم", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "beef stew cubes": {"ar": "مكعبات لحم بقري", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "beef sirloin": {"ar": "ستيك سريلوين بقري", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "beef tenderloin": {"ar": "فيليه بتلو بقري", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "lamb shoulder": {"ar": "كتف ضأن", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "tilapia fillet": {"ar": "فيليه سمك بلطي", "category": "Seafood", "unit": "g", "dietary": "halal,pescatarian"},
    "sea bass": {"ar": "سمك قاروص", "category": "Seafood", "unit": "g", "dietary": "halal,pescatarian"},
    "shrimp": {"ar": "جمبري", "category": "Seafood", "unit": "g", "dietary": "halal,pescatarian"},
    "calamari": {"ar": "حبار كاليماري", "category": "Seafood", "unit": "g", "dietary": "halal,pescatarian"},
    "whole milk": {"ar": "حليب كامل الدسم", "category": "Dairy and Eggs", "unit": "ml", "dietary": "vegetarian,halal"},
    "heavy cream": {"ar": "كريمة طهي", "category": "Dairy and Eggs", "unit": "ml", "dietary": "vegetarian,halal"},
    "butter": {"ar": "زبدة", "category": "Dairy and Eggs", "unit": "g", "dietary": "vegetarian,halal"},
    "ghee": {"ar": "سمن بلدي", "category": "Oils and Fats", "unit": "tablespoon", "dietary": "vegetarian,halal"},
    "eggs": {"ar": "بيض", "category": "Dairy and Eggs", "unit": "piece", "dietary": "vegetarian,halal"},
    "plain yogurt": {"ar": "زبادي طبيعي", "category": "Dairy and Eggs", "unit": "g", "dietary": "vegetarian,halal"},
    "mozzarella cheese": {"ar": "جبنة موتزاريلا", "category": "Cheese", "unit": "g", "dietary": "vegetarian,halal"},
    "parmesan cheese": {"ar": "جبنة بارميزان", "category": "Cheese", "unit": "g", "dietary": "halal"},
    "cheddar cheese": {"ar": "جبنة شيدر", "category": "Cheese", "unit": "slice", "dietary": "vegetarian,halal"},
    "all-purpose flour": {"ar": "دقيق أبيض فاخر", "category": "Flour and Baking", "unit": "g", "dietary": "vegan,halal"},
    "baking powder": {"ar": "بيكنج بودر", "category": "Flour and Baking", "unit": "teaspoon", "dietary": "vegan,halal"},
    "cornstarch": {"ar": "نشا ذرة", "category": "Flour and Baking", "unit": "tablespoon", "dietary": "vegan,gluten-free,halal"},
    "white sugar": {"ar": "سكر أبيض", "category": "Flour and Baking", "unit": "g", "dietary": "vegan,halal"},
    "yellow onion": {"ar": "بصل أصفر", "category": "Vegetables", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "garlic": {"ar": "ثوم", "category": "Vegetables", "unit": "clove", "dietary": "vegan,gluten-free,halal"},
    "red tomato": {"ar": "طماطم حمراء", "category": "Vegetables", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "green bell pepper": {"ar": "فلفل رومي أخضر", "category": "Vegetables", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "green chili pepper": {"ar": "فلفل شطة أخضر", "category": "Vegetables", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "potato": {"ar": "بطاطس", "category": "Vegetables", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "potatoes": {"ar": "بطاطس", "category": "Vegetables", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "carrot": {"ar": "جزر", "category": "Vegetables", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "zucchini": {"ar": "كوسة", "category": "Vegetables", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "black eggplant": {"ar": "باذنجان أسود", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "eggplant": {"ar": "باذنجان رومي", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "fresh molokhia leaves": {"ar": "ملوخية خضراء", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "fresh parsley": {"ar": "بقدونس طازج", "category": "Vegetables", "unit": "bunch", "dietary": "vegan,gluten-free,halal"},
    "fresh dill": {"ar": "شبت طازج", "category": "Vegetables", "unit": "bunch", "dietary": "vegan,gluten-free,halal"},
    "fresh coriander": {"ar": "كزبرة خضراء", "category": "Vegetables", "unit": "bunch", "dietary": "vegan,gluten-free,halal"},
    "lemon": {"ar": "ليمون", "category": "Vegetables", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "fresh mushrooms": {"ar": "مشروم طازج", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "frozen green peas": {"ar": "بسلة خضراء مجمدة", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "green beans": {"ar": "فاصوليا خضراء", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "olive oil": {"ar": "زيت زيتون", "category": "Oils and Fats", "unit": "tablespoon", "dietary": "vegan,gluten-free,halal"},
    "vegetable oil": {"ar": "زيت نباتي", "category": "Oils and Fats", "unit": "tablespoon", "dietary": "vegan,gluten-free,halal"},
    "tomato paste": {"ar": "معجون طماطم", "category": "Condiments and Sauces", "unit": "tablespoon", "dietary": "vegan,gluten-free,halal"},
    "tomato sauce": {"ar": "صلصة طماطم", "category": "Condiments and Sauces", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "tahini": {"ar": "طحينة بيضاء", "category": "Condiments and Sauces", "unit": "tablespoon", "dietary": "vegan,gluten-free,halal"},
    "white vinegar": {"ar": "خل أبيض", "category": "Condiments and Sauces", "unit": "ml", "dietary": "vegan,gluten-free,halal"},
    "cumin": {"ar": "كمون مطحون", "category": "Spices and Seasonings", "unit": "teaspoon", "dietary": "vegan,gluten-free,halal"},
    "coriander": {"ar": "كزبرة مطحونة", "category": "Spices and Seasonings", "unit": "teaspoon", "dietary": "vegan,gluten-free,halal"},
    "dry coriander": {"ar": "كزبرة جافة", "category": "Spices and Seasonings", "unit": "tablespoon", "dietary": "vegan,gluten-free,halal"},
    "turmeric": {"ar": "كركم مطحون", "category": "Spices and Seasonings", "unit": "teaspoon", "dietary": "vegan,gluten-free,halal"},
    "paprika": {"ar": "بابريكا حلوة", "category": "Spices and Seasonings", "unit": "teaspoon", "dietary": "vegan,gluten-free,halal"},
    "black pepper": {"ar": "فلفل أسود", "category": "Spices and Seasonings", "unit": "teaspoon", "dietary": "vegan,gluten-free,halal"},
    "salt": {"ar": "ملح طعام", "category": "Spices and Seasonings", "unit": "tsp", "dietary": "vegan,gluten-free,halal"},
    "fine salt": {"ar": "ملح طعام ناعم", "category": "Spices and Seasonings", "unit": "tsp", "dietary": "vegan,gluten-free,halal"},
    "allspice": {"ar": "بهارات كبابة صيني", "category": "Spices and Seasonings", "unit": "tsp", "dietary": "vegan,gluten-free,halal"},
    "nutmeg": {"ar": "جوزة الطيب", "category": "Spices and Seasonings", "unit": "tsp", "dietary": "vegan,gluten-free,halal"},
    "ground nutmeg": {"ar": "جوزة الطيب مطحونة", "category": "Spices and Seasonings", "unit": "tsp", "dietary": "vegan,gluten-free,halal"},
    "cardamom pods": {"ar": "حبهان حب", "category": "Spices and Seasonings", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "bay leaf": {"ar": "ورق لورا", "category": "Spices and Seasonings", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "dried mint": {"ar": "نعناع مجفف", "category": "Spices and Seasonings", "unit": "tbsp", "dietary": "vegan,gluten-free,halal"},
    "chili pepper powder": {"ar": "شطة حمراء مطحونة", "category": "Spices and Seasonings", "unit": "tsp", "dietary": "vegan,gluten-free,halal"},
    "hot red pepper powder": {"ar": "شطة حمراء حارة", "category": "Spices and Seasonings", "unit": "tsp", "dietary": "vegan,gluten-free,halal"},
    "seven spices": {"ar": "السبع بهارات المصرية", "category": "Spices and Seasonings", "unit": "tsp", "dietary": "vegan,gluten-free,halal"},
    "cinnamon": {"ar": "قرفة مطحونة", "category": "Spices and Seasonings", "unit": "tsp", "dietary": "vegan,gluten-free,halal"},
    "cloves": {"ar": "قرنفل مسمار حب", "category": "Spices and Seasonings", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "mastic gum": {"ar": "مستكة فصوص", "category": "Spices and Seasonings", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "sumac": {"ar": "سماق بلدي", "category": "Spices and Seasonings", "unit": "tbsp", "dietary": "vegan,gluten-free,halal"},
    "ground coriander": {"ar": "كزبرة ناعمة مطحونة", "category": "Spices and Seasonings", "unit": "tsp", "dietary": "vegan,gluten-free,halal"},
    # Breads & Grains
    "baladi bread": {"ar": "عيش بلدي مصري", "category": "Pasta and Grains", "unit": "piece", "dietary": "vegan,halal"},
    "egyptian baladi bread": {"ar": "عيش بلدي مصري", "category": "Pasta and Grains", "unit": "piece", "dietary": "vegan,halal"},
    "shami bread": {"ar": "خبز شامي أبيض", "category": "Pasta and Grains", "unit": "piece", "dietary": "vegan,halal"},
    "toast bread": {"ar": "خبز توست", "category": "Pasta and Grains", "unit": "slice", "dietary": "vegan,halal"},
    "orzo pasta": {"ar": "لسان عصفور", "category": "Pasta and Grains", "unit": "g", "dietary": "vegan,halal"},
    "freekeh": {"ar": "فريك أخضر بلدي", "category": "Pasta and Grains", "unit": "g", "dietary": "vegan,halal"},
    "bulgur": {"ar": "برغل ناعم", "category": "Pasta and Grains", "unit": "g", "dietary": "vegan,halal"},
    "semolina flour": {"ar": "سميد بسبوسة", "category": "Flour and Baking", "unit": "g", "dietary": "vegan,halal"},
    "breadcrumbs": {"ar": "بقسماط ناعم متبل", "category": "Flour and Baking", "unit": "g", "dietary": "vegan,halal"},
    "dry yeast": {"ar": "خميرة فورية جافة", "category": "Flour and Baking", "unit": "tbsp", "dietary": "vegan,gluten-free,halal"},
    "vanilla extract": {"ar": "فانيليا", "category": "Flour and Baking", "unit": "tsp", "dietary": "vegan,gluten-free,halal"},
    "cocoa powder": {"ar": "بودرة كاكاو خام", "category": "Flour and Baking", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "powdered sugar": {"ar": "سكر بودرة منخول", "category": "Flour and Baking", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    # Meats & Poultry
    "beef shank": {"ar": "موزة بقري بالعظم", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "beef liver": {"ar": "كبدة بقري بلدي", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "beef sirloin steak": {"ar": "ستيك سريلوين بقري", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "oxtail": {"ar": "عكاوي بقري", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "pastirma": {"ar": "بسطرمة بلدي متبلة", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "oriental sausage": {"ar": "سجق شرقي بلدي", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "lamb meat cubes": {"ar": "مكعبات لحم ضأن", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "minced lamb": {"ar": "لحم ضأن مفروم", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "pigeon": {"ar": "حمام بلدي مزارع", "category": "Meat and Poultry", "unit": "piece", "dietary": "halal"},
    "whole rabbit": {"ar": "أرنب كامل بلدي", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    "chicken liver": {"ar": "كبدة دجاج طازجة", "category": "Meat and Poultry", "unit": "g", "dietary": "halal"},
    # Seafood
    "whole tilapia": {"ar": "سمك بلطي طازج", "category": "Seafood", "unit": "g", "dietary": "halal,pescatarian"},
    "mackerel": {"ar": "سمك ماكريل", "category": "Seafood", "unit": "g", "dietary": "halal,pescatarian"},
    "mullet": {"ar": "سمك بوري طازج", "category": "Seafood", "unit": "g", "dietary": "halal,pescatarian"},
    "sea bream": {"ar": "سمك دنيس", "category": "Seafood", "unit": "g", "dietary": "halal,pescatarian"},
    "clams": {"ar": "جندوفلي طازج", "category": "Seafood", "unit": "g", "dietary": "halal,pescatarian"},
    "sardines": {"ar": "سردين بلدي", "category": "Seafood", "unit": "g", "dietary": "halal,pescatarian"},
    "canned tuna": {"ar": "تونة معلبة", "category": "Seafood", "unit": "g", "dietary": "halal,pescatarian"},
    # Cheeses & Dairy
    "feta white cheese": {"ar": "جبنة بيضاء فيتا / قريش", "category": "Cheese", "unit": "g", "dietary": "vegetarian,halal"},
    "rumi cheese": {"ar": "جبنة رومي مصرية", "category": "Cheese", "unit": "g", "dietary": "vegetarian,halal"},
    "qashta": {"ar": "قشطة بلدي", "category": "Dairy and Eggs", "unit": "g", "dietary": "vegetarian,halal"},
    # Oils & Sauces
    "extra virgin olive oil": {"ar": "زيت زيتون بكر ممتاز", "category": "Oils and Fats", "unit": "tbsp", "dietary": "vegan,gluten-free,halal"},
    "vegetable cooking oil": {"ar": "زيت طهي نباتي", "category": "Oils and Fats", "unit": "tbsp", "dietary": "vegan,gluten-free,halal"},
    "flaxseed oil": {"ar": "زيت حار بذر الكتان", "category": "Oils and Fats", "unit": "ml", "dietary": "vegan,gluten-free,halal"},
    "strained tomato puree": {"ar": "صلصة طماطم مسبكة", "category": "Condiments and Sauces", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "tahini sesame paste": {"ar": "طحينة سمسم بيضاء", "category": "Condiments and Sauces", "unit": "tbsp", "dietary": "vegan,gluten-free,halal"},
    "pomegranate molasses": {"ar": "دبس رمان طبيعي", "category": "Condiments and Sauces", "unit": "tbsp", "dietary": "vegan,gluten-free,halal"},
    # Vegetables & Fruits
    "white kidney beans": {"ar": "فاصوليا بيضاء جافة", "category": "Legumes and Pulses", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "black-eyed peas": {"ar": "لوبيا بعين سوداء", "category": "Legumes and Pulses", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "green peas": {"ar": "بسلة خضراء", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "taro root": {"ar": "قلقاس بلدي", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "swiss chard": {"ar": "سلق أخضر طازج", "category": "Vegetables", "unit": "bunch", "dietary": "vegan,gluten-free,halal"},
    "fresh spinach": {"ar": "سبانخ خضراء طازجة", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "okra": {"ar": "بامية خضراء", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "sweet potato": {"ar": "بطاطا حلوة", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "fresh cauliflower": {"ar": "قرنبيط طازج", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "white cabbage": {"ar": "كرنب بلدي للمحشي", "category": "Vegetables", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "white eggplant": {"ar": "باذنجان أبيض عروس", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "vine leaves": {"ar": "ورق عنب بناتي", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "cucumber": {"ar": "خيار بلدي طازج", "category": "Vegetables", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "radish": {"ar": "فجل أحمر بلدي", "category": "Vegetables", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "beetroot": {"ar": "بنجر أحمر مسلوق", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "orange": {"ar": "برتقال بلدي", "category": "Vegetables", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "strawberry": {"ar": "فراولة طازجة", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "mango": {"ar": "مانجو بلدي", "category": "Vegetables", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "red onion": {"ar": "بصل أحمر", "category": "Vegetables", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    "celery": {"ar": "كرفس أخضر بلدي", "category": "Vegetables", "unit": "piece", "dietary": "vegan,gluten-free,halal"},
    # Nuts & Dried Fruits
    "raw almonds": {"ar": "لوز ني مقشر", "category": "Flour and Baking", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "walnuts": {"ar": "عين جمل ني", "category": "Flour and Baking", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "pistachios": {"ar": "فستق حلبي", "category": "Flour and Baking", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "pine nuts": {"ar": "صنوبر بلدي", "category": "Flour and Baking", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "coconut flakes": {"ar": "جوز هند مبشور", "category": "Flour and Baking", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "raisins": {"ar": "زبيب ذهبي", "category": "Flour and Baking", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "raw white sesame seeds": {"ar": "سمسم أبيض ني", "category": "Flour and Baking", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    # Beverages & Traditional Infusions
    "dried hibiscus flowers": {"ar": "كركديه أسواني زهرة كاملة", "category": "Condiments and Sauces", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "tamarind pulp": {"ar": "تمر هندي طبيعي", "category": "Condiments and Sauces", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "carob pods": {"ar": "خروب مجروش طبيعي", "category": "Condiments and Sauces", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "dried apricot sheet": {"ar": "قمر الدين مشمش طبيعي", "category": "Condiments and Sauces", "unit": "g", "dietary": "vegan,gluten-free,halal"},
    "egyptian black tea": {"ar": "شاي أسود مصري", "category": "Condiments and Sauces", "unit": "tsp", "dietary": "vegan,gluten-free,halal"}
}


def _canonical_key(name: str) -> str:
    """Normalize string for canonical mapping."""
    clean = re.sub(r"[^\w\s-]", "", str(name).lower())
    clean = " ".join(clean.split()).strip()
    return clean


def build_and_clean_ingredients():
    """Builds ingredients_master.csv and recipe_ingredients_clean.csv."""
    if not RAW_ING_PATH.exists():
        raise FileNotFoundError(f"Recipe ingredients raw file not found at {RAW_ING_PATH}")

    df_raw = pd.read_csv(RAW_ING_PATH, dtype=str, encoding="utf-8-sig")
    logger.info("Loaded %d raw recipe ingredient rows", len(df_raw))

    # Identify ingredient column
    col_name = "original_ingredient_name" if "original_ingredient_name" in df_raw.columns else "ingredient_name"

    # Extract all distinct ingredient names
    unique_names = (
        df_raw[col_name]
        .dropna()
        .str.strip()
        .unique()
        .tolist()
    )
    unique_names.sort(key=lambda s: s.lower())
    logger.info("Found %d distinct ingredient names across recipes", len(unique_names))

    # Build Master Catalog
    master_rows = []
    name_to_id_map = {}

    for idx, raw_name in enumerate(unique_names, start=1):
        ing_id = f"ING{idx:04d}"
        canon_key = _canonical_key(raw_name)
        info = KNOWN_INGREDIENTS.get(canon_key, {})

        # Fallback category inference
        category = info.get("category", "")
        if not category:
            if any(w in canon_key for w in ["meat", "beef", "chicken", "lamb", "duck", "veal"]):
                category = "Meat and Poultry"
            elif any(w in canon_key for w in ["fish", "shrimp", "calamari", "tilapia", "bass", "seafood"]):
                category = "Seafood"
            elif any(w in canon_key for w in ["milk", "cheese", "butter", "cream", "yogurt", "egg"]):
                category = "Dairy and Eggs"
            elif any(w in canon_key for w in ["pasta", "rice", "macaroni", "vermicelli", "noodle"]):
                category = "Pasta and Grains"
            elif any(w in canon_key for w in ["bean", "lentil", "chickpea", "pulse"]):
                category = "Legumes and Pulses"
            elif any(w in canon_key for w in ["oil", "ghee", "fat"]):
                category = "Oils and Fats"
            elif any(w in canon_key for w in ["pepper", "salt", "cumin", "coriander", "turmeric", "cinnamon", "spice"]):
                category = "Spices and Seasonings"
            elif any(w in canon_key for w in ["onion", "garlic", "tomato", "potato", "carrot", "zucchini", "vegetable"]):
                category = "Vegetables"
            else:
                category = "Other"

        ar_name = info.get("ar", "")
        if not ar_name:
            ar_name = normalize_arabic_text(raw_name)

        default_unit = info.get("unit", "g")
        dietary = info.get("dietary", "halal")

        master_rows.append({
            "ingredient_id": ing_id,
            "canonical_name_en": raw_name.title(),
            "canonical_name_ar": ar_name,
            "aliases_en": f"{raw_name.lower()}, {canon_key}",
            "aliases_ar": ar_name,
            "category": category,
            "default_unit": default_unit,
            "alternative_names": canon_key,
            "dietary_tags": dietary
        })
        name_to_id_map[raw_name.strip().lower()] = ing_id

    master_df = pd.DataFrame(master_rows)
    MASTER_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    master_df.to_csv(MASTER_OUT_PATH, index=False, encoding="utf-8-sig")
    logger.info("Saved ingredients master (%d rows) to %s", len(master_df), MASTER_OUT_PATH)

    # Clean and standardize recipe_ingredients
    df_clean_ri = df_raw.copy()
    
    # 1. Normalize quantity
    def _clean_qty(val):
        parsed = normalize_quantity(val)
        return parsed if parsed is not None and parsed > 0 else 1.0

    df_clean_ri["quantity"] = df_clean_ri["quantity"].apply(_clean_qty)

    # 2. Normalize unit
    def _clean_unit(u):
        if not u or str(u).lower() in ["", "nan", "none"]:
            return "piece"
        canon = normalize_unit(str(u))
        return canon if canon else str(u).strip().lower()

    df_clean_ri["unit"] = df_clean_ri["unit"].apply(_clean_unit)

    # 3. Map foreign key ingredient_id
    def _map_ing_id(name):
        return name_to_id_map.get(str(name).strip().lower(), "ING0001")

    df_clean_ri["ingredient_id"] = df_clean_ri[col_name].apply(_map_ing_id)

    # 4. Standardize column names
    df_clean_ri["original_ingredient_name"] = df_clean_ri[col_name].astype(str).str.strip().str.title()
    if "is_optional" not in df_clean_ri.columns:
        df_clean_ri["is_optional"] = 0
    else:
        df_clean_ri["is_optional"] = pd.to_numeric(df_clean_ri["is_optional"], errors="coerce").fillna(0).astype(int)

    if "preparation_note" not in df_clean_ri.columns:
        df_clean_ri["preparation_note"] = ""
    else:
        df_clean_ri["preparation_note"] = df_clean_ri["preparation_note"].fillna("").astype(str).str.strip()

    keep_cols = [
        "recipe_ingredient_id", "recipe_id", "ingredient_id",
        "original_ingredient_name", "quantity", "unit",
        "preparation_note", "is_optional", "source_url"
    ]
    df_clean_ri = df_clean_ri[[c for c in keep_cols if c in df_clean_ri.columns]]

    df_clean_ri.to_csv(CLEAN_RECIPE_ING_PATH, index=False, encoding="utf-8-sig")
    logger.info("Saved clean recipe ingredients (%d rows) to %s", len(df_clean_ri), CLEAN_RECIPE_ING_PATH)

    return master_df, df_clean_ri


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    build_and_clean_ingredients()
