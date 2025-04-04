import pickle
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, LabelEncoder

with open(r"C:\Users\prtyksh\Documents\ai4humanity\pythonBackend\aiStuff\models\severity_model.pkl", "rb") as f:
    severity_model = pickle.load(f)

with open(r"C:\Users\prtyksh\Documents\ai4humanity\pythonBackend\aiStuff\models\time_model.pkl", "rb") as f:
    time_model = pickle.load(f)
disease_severity = {'None':0,
    'Type 2 Diabetes': 3, 'Hypertension': 2, 'Coronary Artery Disease': 4, 'COPD': 4,
    'Chronic Kidney Disease': 4, 'HIV/AIDS': 5, 'Rheumatoid Arthritis': 3, 'Osteoporosis': 2,
    'Asthma': 2, 'COVID-19 (Chronic)': 3, 'Cirrhosis': 5, 'Heart Failure': 4, 'Stroke History': 4,
    'Dementia': 5, 'Epilepsy': 3, 'Psoriasis': 2, 'Lupus': 4, 'Multiple Sclerosis': 4,
    'Parkinson\'s Disease': 4, 'IBD (Crohn\'s/Colitis)': 3, 'Bipolar Disorder': 3,
    'Schizophrenia': 4, 'Sleep Apnea': 2, 'Osteoarthritis': 3, 'Chronic Pancreatitis': 4,
    'Hepatitis C': 3, 'Sickle Cell Anemia': 4, 'Cystic Fibrosis': 5, 'Pulmonary Fibrosis': 4,
    'Thyroid Cancer': 4, 'Breast Cancer': 3, 'Prostate Cancer': 3, 'Melanoma': 4,
    'Glaucoma': 3, 'Macular Degeneration': 3, 'Tuberculosis': 4, 'Chronic Migraine': 3,
    'PTSD': 3, 'Obesity (Class III)': 3, 'Peripheral Neuropathy': 3, 'Gout': 2,
    'Ankylosing Spondylitis': 3, 'Autism Spectrum': 2, 'Fibromyalgia': 3, 'Endometriosis': 3,
    'Chronic Sinusitis': 2, 'Celiac Disease': 2, 'Hemophilia': 4, 'Sarcoidosis': 3,
    'Tinnitus': 2
}
symptoms_data = {
    # Existing Entries (20)
    "Headache": {"Department": "Neurology", "Severity": 4},
    "Fever": {"Department": "General Medicine", "Severity": 3},
    "Cough": {"Department": "Pulmonology", "Severity": 3},
    "Chest Pain": {"Department": "Cardiology", "Severity": 7},
    "Fatigue": {"Department": "General Medicine", "Severity": 4},
    "Shortness of Breath": {"Department": "Pulmonology", "Severity": 8},
    "Dizziness": {"Department": "Neurology", "Severity": 5},
    "Abdominal Pain": {"Department": "Gastroenterology", "Severity": 6},
    "Vomiting": {"Department": "Gastroenterology", "Severity": 5},
    "Joint Pain": {"Department": "Rheumatology", "Severity": 4},
    "Back Pain": {"Department": "Orthopedics", "Severity": 5},
    "Skin Rash": {"Department": "Dermatology", "Severity": 3},
    "Nausea": {"Department": "Gastroenterology", "Severity": 4},
    "Loss of Consciousness": {"Department": "Neurology", "Severity": 9},
    "Blurred Vision": {"Department": "Ophthalmology", "Severity": 6},
    "Hearing Loss": {"Department": "ENT", "Severity": 5},
    "Swelling": {"Department": "General Surgery", "Severity": 5},
    "Palpitations": {"Department": "Cardiology", "Severity": 7},
    "Frequent Urination": {"Department": "Urology", "Severity": 4},
    "Unexplained Weight Loss": {"Department": "Endocrinology", "Severity": 7},
    "Arm Weakness": {"Department": "Neurology", "Severity": 6},
    "Abdominal Distention": {"Department": "Gastroenterology", "Severity": 5},
    "Arrhythmia": {"Department": "Cardiology", "Severity": 8},
    "Anxiety": {"Department": "Psychiatry", "Severity": 5},
    "Breast Lumps": {"Department": "Oncology", "Severity": 7},
    "Bleeding Gums": {"Department": "Dentistry", "Severity": 3},
    "Cold Hands": {"Department": "Vascular Surgery", "Severity": 4},
    "Diarrhea": {"Department": "Gastroenterology", "Severity": 4},
    "Ear Pain": {"Department": "ENT", "Severity": 5},
    "Eye Twitching": {"Department": "Ophthalmology", "Severity": 2},
    "Fainting": {"Department": "Cardiology", "Severity": 6},
    "Flank Pain": {"Department": "Nephrology", "Severity": 7},
    "Glaucoma": {"Department": "Ophthalmology", "Severity": 7},
    "Hemorrhoids": {"Department": "Proctology", "Severity": 4},
    "Insomnia": {"Department": "Psychiatry", "Severity": 5},
    "Jaundice": {"Department": "Hepatology", "Severity": 7},
    "Kidney Pain": {"Department": "Nephrology", "Severity": 6},
    "Limping": {"Department": "Orthopedics", "Severity": 4},
    "Memory Loss": {"Department": "Neurology", "Severity": 7},
    "Night Sweats": {"Department": "General Medicine", "Severity": 5},
    "Ocular Pain": {"Department": "Ophthalmology", "Severity": 6},
    "Pelvic Pain": {"Department": "Gynecology", "Severity": 6},
    "Quivering Lips": {"Department": "Neurology", "Severity": 3},
    "Rectal Bleeding": {"Department": "Proctology", "Severity": 7},
    "Seizures": {"Department": "Neurology", "Severity": 9},
    "Tremors": {"Department": "Neurology", "Severity": 5},
    "Urinary Retention": {"Department": "Urology", "Severity": 6},
    "Vertigo": {"Department": "ENT", "Severity": 5},
    "Wheezing": {"Department": "Pulmonology", "Severity": 6},
    "Xerostomia": {"Department": "Dentistry", "Severity": 3},
    "Yellow Sputum": {"Department": "Pulmonology", "Severity": 5},
    "Zoster Pain": {"Department": "Infectious Disease", "Severity": 6},
    "Burning Urination": {"Department": "Urology", "Severity": 5},
    "Chest Tightness": {"Department": "Cardiology", "Severity": 7},
    "Difficulty Swallowing": {"Department": "Gastroenterology", "Severity": 6},
    "Excessive Thirst": {"Department": "Endocrinology", "Severity": 5},
    "Facial Paralysis": {"Department": "Neurology", "Severity": 8},
    "Gait Abnormalities": {"Department": "Neurology", "Severity": 5},
    "Heartburn": {"Department": "Gastroenterology", "Severity": 4},
    "Itchy Eyes": {"Department": "Ophthalmology", "Severity": 3},
    "Joint Stiffness": {"Department": "Rheumatology", "Severity": 4},
    "Knee Swelling": {"Department": "Orthopedics", "Severity": 5},
    "Leg Cramps": {"Department": "Vascular Surgery", "Severity": 3},
    "Mouth Ulcers": {"Department": "Dentistry", "Severity": 3},
    "Numbness": {"Department": "Neurology", "Severity": 5},
    "Oliguria": {"Department": "Nephrology", "Severity": 6},
    "Postnasal Drip": {"Department": "ENT", "Severity": 3},
    "Rhinorrhea": {"Department": "ENT", "Severity": 3},
    "Sore Throat": {"Department": "ENT", "Severity": 4},
    "Tinnitus": {"Department": "ENT", "Severity": 4},
    "Urinary Incontinence": {"Department": "Urology", "Severity": 5},
    "Visual Floaters": {"Department": "Ophthalmology", "Severity": 4},
    "Wrist Pain": {"Department": "Orthopedics", "Severity": 4},
    "Xerophthalmia": {"Department": "Ophthalmology", "Severity": 3},
    "Yawning Spells": {"Department": "Neurology", "Severity": 3},
    "Air Hunger": {"Department": "Pulmonology", "Severity": 7},
    "Bradycardia": {"Department": "Cardiology", "Severity": 6},
    "Constipation": {"Department": "Gastroenterology", "Severity": 3},
    "Dysphagia": {"Department": "Gastroenterology", "Severity": 6},
    "Epistaxis": {"Department": "ENT", "Severity": 4},
    "Fasciculations": {"Department": "Neurology", "Severity": 4},
    "Gingivitis": {"Department": "Dentistry", "Severity": 3},
    "Hemoptysis": {"Department": "Pulmonology", "Severity": 8},
    "Hypotension": {"Department": "Cardiology", "Severity": 6},
    "Impetigo": {"Department": "Dermatology", "Severity": 3},
    "Jaw Pain": {"Department": "Dentistry", "Severity": 4},
    "Kyphosis": {"Department": "Orthopedics", "Severity": 5},
    "Lymphadenopathy": {"Department": "Hematology", "Severity": 5},
    "Melena": {"Department": "Gastroenterology", "Severity": 7},
    "Nocturia": {"Department": "Urology", "Severity": 4},
    "Onycholysis": {"Department": "Dermatology", "Severity": 2},
    "Paresthesia": {"Department": "Neurology", "Severity": 5},
    "Quadriparesis": {"Department": "Neurology", "Severity": 8},
    "Restless Legs": {"Department": "Neurology", "Severity": 4},
    "Scleral Icterus": {"Department": "Hepatology", "Severity": 6},
    "Tachycardia": {"Department": "Cardiology", "Severity": 7},
    "Urticaria": {"Department": "Allergy", "Severity": 4},
    "Vaginal Bleeding": {"Department": "Gynecology", "Severity": 6},
    "Wheals": {"Department": "Allergy", "Severity": 4},
    "Xanthelasma": {"Department": "Endocrinology", "Severity": 3},
    "Yersiniosis": {"Department": "Infectious Disease", "Severity": 5},
    "Zinc Deficiency": {"Department": "Nutrition", "Severity": 3},
    "Anal Fissure": {"Department": "Proctology", "Severity": 4},
    "Bunion Pain": {"Department": "Orthopedics", "Severity": 3},
    "Cataract Symptoms": {"Department": "Ophthalmology", "Severity": 4},
    "Dyspareunia": {"Department": "Gynecology", "Severity": 5},
    "Erectile Dysfunction": {"Department": "Urology", "Severity": 4},
    "Foot Drop": {"Department": "Neurology", "Severity": 5},
    "Gastroesophageal Reflux": {"Department": "Gastroenterology", "Severity": 4},
    "Hyperhidrosis": {"Department": "Dermatology", "Severity": 3},
    "Iritis": {"Department": "Ophthalmology", "Severity": 5},
    "Jaundice (Neonatal)": {"Department": "Pediatrics", "Severity": 6},
    "Kernicterus": {"Department": "Neonatology", "Severity": 8},
    "Laryngitis": {"Department": "ENT", "Severity": 4},
    "Myalgia": {"Department": "Rheumatology", "Severity": 4},
    "Nystagmus": {"Department": "Neurology", "Severity": 5},
    "Osteopenia": {"Department": "Orthopedics", "Severity": 4},
    "Priapism": {"Department": "Urology", "Severity": 7},
    "Quadriceps Pain": {"Department": "Orthopedics", "Severity": 4},
    "Radiculopathy": {"Department": "Neurology", "Severity": 6},
    "Splenomegaly": {"Department": "Hematology", "Severity": 6},
    "Torticollis": {"Department": "Orthopedics", "Severity": 4},
    "Uveitis": {"Department": "Ophthalmology", "Severity": 6},
    "Vitiligo": {"Department": "Dermatology", "Severity": 3},
    "Wernicke's Aphasia": {"Department": "Neurology", "Severity": 7},
    "Xiphoid Pain": {"Department": "General Surgery", "Severity": 4},
    "Yersinia Symptoms": {"Department": "Infectious Disease", "Severity": 5},
    "Zygoma Pain": {"Department": "Dentistry", "Severity": 3}
}

def getSeverityAndTime(age, gender, previousVisits, symptoms, medicalHistory, department):
    data = pd.DataFrame({
    'Age': [age],
    'Gender': gender,
    'Previous_Visits': [previousVisits],
    'Symptoms': symptoms,
    'Prev_Disease': medicalHistory,
    'Department': department,
    
    })
    data["Prev_Severity"] = [disease_severity[disease] for disease in data['Prev_Disease']]

    data['Gender'] = data['Gender'].map({'Male': 0, 'Female': 1})
    data['Department'] = data['Symptoms'].map(lambda x: symptoms_data[x]['Department'])

    symptom_encoder = LabelEncoder()
    data['Symptoms'] = symptom_encoder.fit_transform(data['Symptoms'])

    dept_encoder = LabelEncoder()
    data['Department'] = dept_encoder.fit_transform(data['Department'])
    X_severity = data[['Age', 'Gender', 'Previous_Visits', 'Symptoms','Prev_Severity']]

    predicted_severity = severity_model.predict(X_severity)


    data['Predicted_Severity'] = predicted_severity
    X_time = data[['Predicted_Severity', 'Department','Age', 'Gender', 'Previous_Visits', 'Symptoms']]

    predicted_time = time_model.predict(X_time)
    return predicted_severity[0], predicted_time[0]
  
