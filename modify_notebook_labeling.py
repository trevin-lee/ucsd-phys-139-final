import json

nb_path = 'notebooks/generate_labeled_dataset.ipynb'

with open(nb_path, 'r') as f:
    nb = json.load(f)

# Keep imports (Cell 0) but update it to be cleaner if needed
# We will construct new cells list

# Cell 0: Imports and Paths
cell_imports = nb['cells'][0]
# We'll make sure the user knows where to specify the file
source_imports = [
    "import numpy as np\n",
    "import pandas as pd \n",
    "from pathlib import Path\n",
    "\n",
    "# Paths\n",
    "DATA_DIR = Path(\"/home/admin/main/ucsd-phys-139-final/data\")\n",
    "\n",
    "# --- SPECIFY YOUR FEATURES FILE HERE ---\n",
    "FEATURES_FILENAME = \"features.csv\"\n",
    "FEATURES_PATH = DATA_DIR / FEATURES_FILENAME\n",
    "\n",
    "LABELED_FEATURES_PATH = DATA_DIR / \"labeled_features.csv\"\n",
    "\n",
    "# Cross-match paths\n",
    "GAIA_MATCH = DATA_DIR / \"gaia_crossmatch/gaia_crossmatch.csv\"\n",
    "ASASSN_MATCH = DATA_DIR / \"asassn/asassn_crossmatch.csv\"\n"
]
cell_imports['source'] = source_imports

# Cell 1: Load Features
cell_load = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# 1. Load Existing Features\n",
        "if FEATURES_PATH.exists():\n",
        "    print(f\"Loading features from {FEATURES_PATH}...\")\n",
        "    df_features = pd.read_csv(FEATURES_PATH)\n",
        "    print(f\"Loaded {len(df_features)} rows.\")\n",
        "    print(\"Columns:\", df_features.columns.tolist())\n",
        "else:\n",
        "    raise FileNotFoundError(f\"Features file not found at {FEATURES_PATH}\")\n"
    ]
}

# Cell 2: Load Cross-Match
cell_crossmatch = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# 2. Load Cross-Match Results\n",
        "gaia_df = pd.read_csv(GAIA_MATCH) if GAIA_MATCH.exists() else pd.DataFrame()\n",
        "asassn_df = pd.read_csv(ASASSN_MATCH) if ASASSN_MATCH.exists() else pd.DataFrame()\n",
        "\n",
        "print(f\"Loaded {len(gaia_df)} Gaia matches\")\n",
        "print(f\"Loaded {len(asassn_df)} ASASSN matches\")\n"
    ]
}

# Cell 3: Label and Save
cell_label = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# 3. Add Label Column\n",
        "df_features['label'] = 'Unknown'\n",
        "\n",
        "# We need 'star_id' to match against the cross-match results\n",
        "if 'star_id' in df_features.columns:\n",
        "    # 3a. Merge ASASSN Class\n",
        "    if not asassn_df.empty:\n",
        "        # ASASSN crossmatch has 'TESS file name' and 'ASASSN Class'\n",
        "        # Map TESS filename to ASASSN Class\n",
        "        asassn_map = dict(zip(asassn_df['TESS file name'], asassn_df['ASASSN Class']))\n",
        "        \n",
        "        # Update labels where we have a match\n",
        "        df_features['label'] = df_features['star_id'].map(asassn_map).fillna(df_features['label'])\n",
        "        \n",
        "    # 3b. Merge Gaia Class (if available)\n",
        "    if not gaia_df.empty and 'Gaia_Class' in gaia_df.columns:\n",
        "        # Map TESS Filename to Gaia Class. \n",
        "        # Priority: ASASSN > Gaia. Only update if still Unknown.\n",
        "        gaia_map = dict(zip(gaia_df['TESS_Filename'], gaia_df['Gaia_Class']))\n",
        "        \n",
        "        mask_unknown = df_features['label'] == 'Unknown'\n",
        "        new_labels = df_features.loc[mask_unknown, 'star_id'].map(gaia_map)\n",
        "        df_features.loc[mask_unknown, 'label'] = new_labels.fillna('Unknown')\n",
        "else:\n",
        "    print(\"Warning: 'star_id' column not found in features. Cannot match labels automatically.\")\n",
        "\n",
        "# Save the labeled dataset\n",
        "df_features.to_csv(LABELED_FEATURES_PATH, index=False)\n",
        "print(f\"Saved labeled features to {LABELED_FEATURES_PATH}\")\n",
        "print(\"Label distribution:\")\n",
        "print(df_features['label'].value_counts())\n"
    ]
}

# Reassemble notebook
nb['cells'] = [cell_imports, cell_load, cell_crossmatch, cell_label]

with open(nb_path, 'w') as f:
    json.dump(nb, f, indent=1)

print("Notebook modified to load features and apply labels.")

