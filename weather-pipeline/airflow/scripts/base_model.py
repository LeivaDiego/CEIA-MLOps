# Definición de un modelo base para predicción de lluvia

# --- Librerías ---
from sklearn.ensemble import RandomForestClassifier

# --- Funciones ---

def get_base_model():
    """
    Retorna un modelo base de Random Forest para predicción de lluvia.

    Args:
        None

    Returns:
        model: Un modelo RandomForestClassifier de scikit-learn.
    """
    model = RandomForestClassifier(
        n_estimators=100,       # 100 árboles
        max_depth=None,         # Sin límite de profundidad
        min_samples_split=2,    # División estándar
        min_samples_leaf=1,     # Mínima cantidad de hojas
        random_state=42,        # Para resultados reproducibles
        n_jobs=-1               # Usa todos los núcleos disponibles
    )
    return model
