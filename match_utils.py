# match_utils.py
import pandas as pd
from thefuzz import process
import os

DB_PATH = os.path.join("database", "medicines.csv")


def load_database(path=DB_PATH):
    """Load medicines database CSV, ensuring all values are strings."""
    if not os.path.exists(path):
        return pd.DataFrame(columns=[
            "name", "manufacturer", "uses", "dosage",
            "side_effects", "more_info_url", "barcode"
        ])
    df = pd.read_csv(path)
    for c in df.columns:
        df[c] = df[c].fillna("").astype(str)
    return df


def match_medicine_name(query, df=None, top_k=3):
    """
    Match medicine name or barcode using fuzzy matching.
    
    query: string to match
    df: medicines database (DataFrame)
    top_k: number of results to return

    returns: list of dicts with medicine details and match score
    """
    if df is None:
        df = load_database()
    if df.empty:
        return []

    query = (query or "").strip()
    if not query:
        return []

    # Exact match by barcode
    if 'barcode' in df.columns and query in df['barcode'].values:
        row = df[df['barcode'] == query].iloc[0]
        return [{
            'name': row['name'],
            'score': 100,
            'manufacturer': row.get('manufacturer', ''),
            'uses': row.get('uses', ''),
            'dosage': row.get('dosage', ''),
            'side_effects': row.get('side_effects', ''),
            'more_info_url': row.get('more_info_url', ''),
            'barcode': row.get('barcode', ''),
        }]

    # Prepare choices for fuzzy matching
    indexed_choices = {
        i: f"{row['name']} {row.get('manufacturer', '')}"
        for i, row in df.iterrows()
    }

    results = process.extract(query, indexed_choices, limit=top_k)

    output = []
    for match_text, score, idx in results:
        if idx not in indexed_choices:
            continue
        row = df.iloc[idx]
        output.append({
            'name': row['name'],
            'score': score,
            'manufacturer': row.get('manufacturer', ''),
            'uses': row.get('uses', ''),
            'dosage': row.get('dosage', ''),
            'side_effects': row.get('side_effects', ''),
            'more_info_url': row.get('more_info_url', ''),
            'barcode': row.get('barcode', ''),
        })

    return output
