import os
import subprocess
from dotenv import load_dotenv

def run_command(command):
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(f"Success: {result.stdout}")
    return result.returncode

def main():
    load_dotenv()
    
    bucket = os.getenv("SUPABASE_S3_BUCKET")
    endpoint = os.getenv("SUPABASE_S3_ENDPOINT")
    access_key = os.getenv("SUPABASE_S3_ACCESS_KEY_ID")
    secret_key = os.getenv("SUPABASE_S3_SECRET_ACCESS_KEY")
    region = os.getenv("SUPABASE_S3_REGION", "us-east-1")

    if not all([bucket, endpoint, access_key, secret_key]):
        print("Faltan variables de entorno para S3 en el .env")
        return

    # 1. Configurar el remoto principal
    run_command(f"dvc remote add -d -f storage s3://{bucket}")
    
    # 2. Configurar el endpoint
    run_command(f"dvc remote modify storage endpointurl {endpoint}")
    
    # 3. Configurar la región
    run_command(f"dvc remote modify storage region {region}")

    # 4. Configurar credenciales (Localmente para no subir al config de git)
    run_command(f"dvc remote modify --local storage access_key_id {access_key}")
    run_command(f"dvc remote modify --local storage secret_access_key {secret_key}")

    print("\n--- DVC Remote Configuration Completed ---")
    run_command("dvc remote list")

if __name__ == "__main__":
    main()
