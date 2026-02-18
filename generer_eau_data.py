import pandas as pd
import numpy as np

# --- CONFIGURATION ---
NUM_POINTS = 300
FILENAME = "Water_Data_Marrakech_Safi.csv"

# Geographic Bounds for Marrakech-Safi (Approximate)
LAT_MIN, LAT_MAX = 31.20, 32.50
LON_MIN, LON_MAX = -9.80, -7.30

# Types of Infrastructure
TYPES = ["Barrage (Dam)", "Forage (Well)", "Station Épuration", "Zone Agricole"]
STATUSES = ["Opérationnel", "Critique (Sec)", "En Maintenance", "Pollué"]

# --- GENERATION ---
np.random.seed(42) # For reproducible results

data = []

for i in range(NUM_POINTS):
    type_inf = np.random.choice(TYPES, p=[0.05, 0.6, 0.15, 0.2]) # Mostly Wells & Agriculture
    
    # Logic: Status depends on type
    if type_inf == "Barrage (Dam)":
        level = np.random.randint(5, 100) # Percentage full
        status = "Critique (Sec)" if level < 15 else "Opérationnel"
        name = f"Barrage Loc-{i}"
    elif type_inf == "Forage (Well)":
        level = np.random.randint(0, 50) # Depth in meters
        status = np.random.choice(STATUSES, p=[0.6, 0.2, 0.1, 0.1])
        name = f"Puits Douar-{i}"
    else:
        level = 0
        status = np.random.choice(["Actif", "À l'arrêt"])
        name = f"Zone-{i}"

    # Generate coordinates with a slight cluster around Marrakech (31.6, -8.0)
    lat = np.random.uniform(LAT_MIN, LAT_MAX)
    lon = np.random.uniform(LON_MIN, LON_MAX)

    data.append([
        name, type_inf, status, level, lat, lon
    ])

# --- SAVE ---
df = pd.DataFrame(data, columns=["Nom", "Type", "Statut", "Niveau_Ou_Debit", "lat", "lon"])
df.to_csv(FILENAME, index=False, sep=";")
print(f"✅ GIS Data Generated: {FILENAME}")