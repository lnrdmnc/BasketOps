import pandas as pd
import numpy as np

def calculate_advanced_stats(shots_list):
    """
    Calcola le statistiche avanzate (punti attesi ed eFG%) partendo dalla lista dei tiri.
    """
    if not shots_list:
        return {"efg_pct": 0, "expected_points": 0, "total_shots": 0}
        
    df = pd.DataFrame(shots_list)
    total_shots = len(df)
    made_shots = df[df['made'] == True].shape[0]
    
    # Identifichiamo i tiri da 3 punti (nella NBA la linea è a 23.75 piedi, ovvero 237.5 decimi di piede)
    # Per semplicità usiamo la colonna 'distance' fornita dall'API (espressa in piedi)
    df['is_three'] = df['distance'] >= 23.75
    three_made = df[(df['made'] == True) & (df['is_three'] == True)].shape[0]
    
    # Formula Effective Field Goal Percentage: (Completi + 0.5 * Tripli_Segnati) / Tentati
    efg_pct = ((made_shots + 0.5 * three_made) / total_shots) * 100 if total_shots > 0 else 0
    
    # Punti Totali Generati (2 punti per i tiri normali, 3 per i tiri da tre)
    total_points = ((made_shots - three_made) * 2) + (three_made * 3)
    expected_points_per_shot = total_points / total_shots if total_shots > 0 else 0
    
    return {
        "total_shots": total_shots,
        "made_shots": made_shots,
        "efg_pct": round(efg_pct, 2),
        "expected_points_per_shot": round(expected_points_per_shot, 2)
    }

def generate_heatmap_data(shots_list):
    """
    Raggruppa i tiri in una griglia bidimensionale per creare l'effetto Heatmap (densità di tiro).
    """
    if not shots_list:
        return []
        
    df = pd.DataFrame(shots_list)
    
    # Arrotondiamo le coordinate per raggruppare i tiri in "mattonelle" di campo (es. 20x20 decimi di piede)
    df['x_bin'] = (df['x'] // 20) * 20
    df['y_bin'] = (df['y'] // 20) * 20
    
    # Calcoliamo quanti tiri sono stati tentati e quanti segnati in ogni mattonella
    heatmap_df = df.groupby(['x_bin', 'y_bin']).agg(
        tiri_tentati=('made', 'count'),
        tiri_segnati=('made', lambda x: x.sum())
    ).reset_index()
    
    # Calcoliamo la percentuale di realizzazione per ogni zona
    heatmap_df['pct'] = (heatmap_df['tiri_segnati'] / heatmap_df['tiri_tentati']) * 100
    
    return heatmap_df.to_dict(orient='records')