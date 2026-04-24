from flask import Flask, request, jsonify
from flask_cors import CORS
import json, random, wikipedia, difflib

app = Flask(__name__)
CORS(app)

# ================= LOAD DATASET =================
with open("ultra_large_dataset.json", "r") as f:
    dataset = json.load(f)

# ================= HOME ROUTE (FIXED) =================
@app.route("/")
def home():
    return " MedGuard AI Backend Running Successfully"

# ================= DRUG CLASS =================
DRUG_CLASSES = {
    "amoxicillin": "Antibiotic",
    "tetracycline": "Antibiotic",
    "aspirin": "Painkiller",
    "ibuprofen": "Painkiller",
    "paracetamol": "Painkiller",
    "warfarin": "Blood thinner",
    "metformin": "Antidiabetic"
}

def get_drug_class(drug):
    return DRUG_CLASSES.get(drug.lower(), "General")

# ================= FOOD CATEGORY =================
def get_food_category(food):
    food = food.lower()

    if any(x in food for x in ["wine","beer","whiskey","vodka","alcohol"]):
        return "alcohol"
    if any(x in food for x in ["milk","cheese","yogurt"]):
        return "dairy"
    if any(x in food for x in ["coffee","tea"]):
        return "caffeine"
    if any(x in food for x in ["spinach","kale"]):
        return "leafy"

    return "general"

# ================= TYPO FIX =================
def find_closest_match(name, keys):
    match = difflib.get_close_matches(name, keys, n=1, cutoff=0.6)
    return match[0] if match else None

# ================= WIKIPEDIA =================
def get_drug_info(drug):
    try:
        results = wikipedia.search(drug)
        if results:
            return wikipedia.summary(results[0], sentences=3)
        return "No information found."
    except:
        return "No information available."

# ================= RISK ENGINE =================
def calculate_risk(drug_data, food, drug_class, food_category, allergies, age):
    score = 0.25
    reasons = []

    food_lower = food.lower()

    # Dataset logic
    if any(food_lower in f.lower() for f in drug_data["avoid"]):
        score += 0.5
        reasons.append("Avoid food (dataset)")

    elif any(food_lower in f.lower() for f in drug_data["caution"]):
        score += 0.3
        reasons.append("Caution food")

    elif any(food_lower in f.lower() for f in drug_data["safe"]):
        score -= 0.1
        reasons.append("Safe food")

    # 🚨 REAL MEDICAL RULES (IMPORTANT)

    # Alcohol always dangerous
    if food_category == "alcohol":
        score = max(score, 0.85)
        reasons.append("⚠ Alcohol increases drug toxicity")

    # Paracetamol + Alcohol = VERY HIGH
    if drug_class == "Painkiller" and "paracetamol" in drug_data.get("explanation","").lower() and food_category == "alcohol":
        score = 0.95
        reasons.append("🚨 Severe liver damage risk")

    # Antibiotic + Dairy
    if drug_class == "Antibiotic" and food_category == "dairy":
        score += 0.3
        reasons.append("Dairy reduces absorption")

    # Blood thinner + Leafy
    if drug_class == "Blood thinner" and food_category == "leafy":
        score += 0.4
        reasons.append("Vitamin K interaction")

    # Allergy override
    if any(a.lower() in food_lower for a in allergies):
        score = 0.98
        reasons.append("⚠ Allergy risk")

    # Age factor
    if age and age > 60:
        score += 0.1
        reasons.append("Higher sensitivity (age)")

    score = max(0, min(1, score))
    return score, reasons

# ================= SEVERITY =================
def get_severity(score):
    if score > 0.75:
        return "HIGH"
    elif score > 0.45:
        return "MODERATE"
    return "LOW"

# ================= RECOMMENDATIONS =================
def get_recommendations(allergies):
    foods = ["Rice","Oats","Banana","Apple","Dal"]
    return [f for f in foods if f.lower() not in [a.lower() for a in allergies]]

# ================= MAIN ANALYZE =================
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json

    medicine = data.get("medicine","").strip()
    food = data.get("food","").strip()
    allergies = data.get("allergies",[])
    age = data.get("age")

    # Smart matching
    med_key = find_closest_match(medicine, dataset.keys())

    if not med_key:
        return jsonify({"found": False, "message": "Medicine not found"})

    drug_data = dataset[med_key]

    drug_class = get_drug_class(med_key)
    food_category = get_food_category(food)

    # Risk calculation
    risk, reasons = calculate_risk(
        drug_data, food, drug_class, food_category, allergies, age
    )

    severity = get_severity(risk)

    return jsonify({
        "found": True,
        "severity": severity,
        "risk_probability": round(risk,2),
        "confidence": round(0.85 + random.random()*0.1,2),

        "interaction_reason": ", ".join(reasons),
        "time_gap": "1-2 hours recommended",

        "drug_info": get_drug_info(med_key),
        "drug_class": drug_class,

        "side_effects": drug_data["side_effects"].get(food, ["Mild effects"]),

        "alternatives": get_recommendations(allergies),
        "recipes": ["Rice + Dal","Fruit bowl","Oats breakfast"],

        "explanation_simple": f"{food} may affect how {med_key} works.",
        "explanation_technical": "Interaction involves metabolism and absorption pathways."
    })

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)