# seed_db.py
import asyncio
import motor.motor_asyncio

async def seed_module_8_database():
    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://24je0608_db_user:Dakshta%401234@cluster0.n7xgc4b.mongodb.net/?appName=Cluster0")
    db = client["MedicalCopilotDB"]
    
    # Clear existing data for a clean slate
    await db.associated_symptoms.delete_many({})
    await db.differential_diagnoses.delete_many({})
    
    # 1. Differential Diagnoses Entity (Base Prevalences)
    diagnoses = [
        {"disease": "Malaria", "base_prevalence": 0.05, "urgency": "High"},
        {"disease": "Dengue", "base_prevalence": 0.04, "urgency": "High"},
        {"disease": "Typhoid", "base_prevalence": 0.03, "urgency": "Moderate"}
    ]
    
    # 2. Associated Symptoms Entity (Bayesian Sensitivities)
    symptoms = [
        {"disease": "Malaria", "symptom": "rigors", "sensitivity": 0.85},
        {"disease": "Malaria", "symptom": "sweating", "sensitivity": 0.80},
        {"disease": "Dengue", "symptom": "retro-orbital pain", "sensitivity": 0.90},
        {"disease": "Dengue", "symptom": "rash", "sensitivity": 0.70},
        {"disease": "Typhoid", "symptom": "abdominal pain", "sensitivity": 0.65},
        {"disease": "Typhoid", "symptom": "headache", "sensitivity": 0.70}
    ]
    
    await db.differential_diagnoses.insert_many(diagnoses)
    await db.associated_symptoms.insert_many(symptoms)
    print("Module 8 Database perfectly seeded!")

if __name__ == "__main__":
    asyncio.run(seed_module_8_database())