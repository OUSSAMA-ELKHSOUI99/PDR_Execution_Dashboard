import pandas as pd
import random
from datetime import datetime, timedelta

# --- CONFIGURATION ---
NUM_PROJECTS = 500
FILENAME = "PDR_Marrakech_Safi_Projects.csv"

# Real administrative data for the region
PROVINCES = [
    "Préfecture de Marrakech", "Province de Chichaoua", "Province d'Al Haouz",
    "Province d'El Kelâa des Sraghna", "Province d'Essaouira", "Province de Rehamna",
    "Province de Safi", "Province de Youssoufia"
]

SECTORS = [
    "Infrastructure Routière", "Eau & Assainissement", "Éducation & Formation",
    "Santé", "Tourisme & Artisanat", "Agriculture Solidaire", "Énergie Renouvelable"
]

STATUSES = ["En Étude", "Appel d'Offres", "En Cours", "En Retard", "Achevé", "Suspendu"]

# Vocabulary to build realistic project names
ACTIONS = ["Construction de", "Aménagement de", "Réhabilitation de", "Équipement de", "Étude technique pour"]
TARGETS = ["la route provinciale", "un centre de santé", "une école communale", "un barrage collinaire", "un centre culturel", "un réseau d'eau potable"]

def generate_project_name(sector):
    """Generates a bureaucratic-sounding project name."""
    action = random.choice(ACTIONS)
    if sector == "Infrastructure Routière":
        target = f"la route RP-{random.randint(1000, 9999)}"
    elif sector == "Eau & Assainissement":
        target = f"un système d'alimentation en eau potable (Douar {random.randint(1, 50)})"
    elif sector == "Éducation & Formation":
        target = "un collège de proximité"
    else:
        target = random.choice(TARGETS)
    return f"{action} {target}"

def generate_dates():
    """Generates a start date between 2022 and 2026, and an end date."""
    start_date = datetime(2022, 1, 1) + timedelta(days=random.randint(0, 1000))
    duration = random.randint(90, 730) # 3 months to 2 years
    end_date = start_date + timedelta(days=duration)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

# --- GENERATION LOOP ---
data = []

for i in range(NUM_PROJECTS):
    province = random.choice(PROVINCES)
    sector = random.choice(SECTORS)
    status = random.choice(STATUSES)
    
    # Logic: Budget depends on sector (Infrastructure is expensive)
    if sector in ["Infrastructure Routière", "Eau & Assainissement"]:
        budget = random.randint(2_000_000, 50_000_000) # 2M to 50M DH
    else:
        budget = random.randint(500_000, 5_000_000) # 500k to 5M DH
        
    # Logic: Completion rate depends on status
    if status == "Achevé":
        completion = 100
    elif status == "En Étude" or status == "Appel d'Offres":
        completion = 0
    else:
        completion = random.randint(10, 95)

    start, end = generate_dates()

    data.append([
        f"PRJ-{2024000+i}", # ID
        generate_project_name(sector), # Project Name
        province, # Province
        sector, # Sector
        budget, # Budget (DH)
        status, # Status
        completion, # Completion %
        start, # Start Date
        end # End Date
    ])

# --- SAVE TO CSV ---
df = pd.DataFrame(data, columns=[
    "ID_Projet", "Intitulé_Projet", "Province", "Secteur", 
    "Budget_DH", "Statut", "Taux_Avancement", "Date_Début", "Date_Fin_Prévue"
])

# Save specifically for Excel usage (utf-8-sig handles French accents correctly)
df.to_csv(FILENAME, index=False, encoding='utf-8-sig', sep=';')

print(f"✅ Success! File '{FILENAME}' generated with {NUM_PROJECTS} rows.")
print("You can now open this in Excel, PowerBI, or load it into a Dashboard.")