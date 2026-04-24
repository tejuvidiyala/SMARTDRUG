import json
import random

# ================= Foods =================
foods = []

for i in range(1, 1401):
    foods.append(f"FoodItem_{i}")

real_foods = [
    {"name":"Rice","category":"grain"},
    {"name":"Milk","category":"dairy"},
    {"name":"Cheese","category":"dairy"},
    {"name":"Spinach","category":"leafy"},
    {"name":"Kale","category":"leafy"},
    {"name":"Chicken","category":"protein"},
    {"name":"Egg","category":"protein"},
    {"name":"Alcohol","category":"alcohol"},
    {"name":"Grapefruit","category":"citrus"},
    {"name":"Orange","category":"citrus"},
    {"name":"Coffee","category":"caffeine"},
    {"name":"Tea","category":"caffeine"},
    {"name":"Garlic","category":"spice"},
    {"name":"Ginger","category":"spice"}
]

foods.extend([f["name"] for f in real_foods])

# ================= Medicines =================
medicines = [f"Tablet_{i}" for i in range(1, 2001)]

real_meds = [
    "Amoxicillin","Warfarin","Metformin","Aspirin",
    "Ibuprofen","Tetracycline","Paracetamol"
]
medicines.extend(real_meds)

# ================= Dataset =================
dataset = {}

SIDE_EFFECT_LIST = [
    "Nausea","Dizziness","Headache",
    "Reduced absorption","Increased toxicity"
]

for drug in medicines:

    # Avoid foods
    avoid = random.sample(foods, random.randint(5, 15))

    # Remove avoid items before choosing others
    remaining_foods = list(set(foods) - set(avoid))

    # Caution foods
    caution = random.sample(remaining_foods, random.randint(5, 15))

    # Remove again
    remaining_foods = list(set(remaining_foods) - set(caution))

    # Safe foods
    safe = random.sample(remaining_foods, random.randint(15, 30))

    # Side effects only for avoid & caution
    side_effects = {}

    for f in avoid + caution:
        side_effects[f] = random.sample(
            SIDE_EFFECT_LIST,
            k=random.randint(1,2)
        )

    dataset[drug] = {
        "avoid": avoid,
        "caution": caution,
        "safe": safe,
        "side_effects": side_effects,
        "explanation": f"{drug} may interact with certain foods affecting absorption or metabolism."
    }

# ================= Save =================
with open("ultra_large_dataset.json", "w") as f:
    json.dump(dataset, f, indent=2)

print(" Clean dataset generated (no overlaps + better logic)")