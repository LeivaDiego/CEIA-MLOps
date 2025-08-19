from cryptography.fernet import Fernet
import os

def generate_fernet_key():
    # Generar nueva clave
    key = Fernet.generate_key().decode()
    print(f"SUCCESS | Nueva Fernet Key generada:\n\t{key}")

    # Ruta al archivo .env (uno arriba de /src/)
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '../.env'))

    # Verificar si ya existe la variable
    existing_lines = []
    key_exists = False

    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            existing_lines = f.readlines()
            key_exists = any(line.strip().startswith("AIRFLOW__CORE__FERNET_KEY=") for line in existing_lines)

    if key_exists:
        choice = input("\nWARNING | Ya existe una clave Fernet en el archivo .env \n\t¿Deseas sobrescribirla? (s/n): ").strip().lower()
        if choice != 's':
            print("\nINFO | No se modificó el archivo .env \n\tPuedes copiar la clave manualmente si lo deseas.")
            return
        # Sobrescribir línea existente
        updated_lines = [
            f"\nAIRFLOW__CORE__FERNET_KEY=\"{key}\"\n" if line.startswith("AIRFLOW__CORE__FERNET_KEY=") else line
            for line in existing_lines
        ]
        with open(env_path, 'w') as f:
            f.writelines(updated_lines)
        print(f"\nSUCCESS | Clave actualizada exitosamente en: {env_path}")

    else:
        choice = input(f"\nINFO | No existe una clave en {env_path}. \n\t¿Deseas guardarla allí? (s/n): ").strip().lower()
        if choice != 's':
            print("\nINFO | Puedes copiar la clave manualmente y colocarla en un archivo .env")
            return
        # Crear archivo si no existe, o agregar la línea
        existing_lines.append(f"\nAIRFLOW__CORE__FERNET_KEY=\"{key}\"\n")
        with open(env_path, 'w') as f:
            f.writelines(existing_lines)
        print(f"\nSUCCESS | Clave guardada correctamente en: {env_path}")

if __name__ == "__main__":
    generate_fernet_key()
