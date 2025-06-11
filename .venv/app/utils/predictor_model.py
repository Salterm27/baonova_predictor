import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import joblib


def get_prediction (json_generado):
    with open(os.path.join('/form_types.json'), 'r') as f:
        form_types = json.load(f)
    loaded_model = joblib.load('/best_model.pkl')
    df_generado = pd.DataFrame(json_generado, index=[0])
    df_generado = df_generado.reindex(columns=columns)
    for col in df_generado.columns:
        df_generado[col] = df_generado[col].astype(form_types[col])
    return loaded_model.predict_proba(df_generado)[:, 1]