"""
Script de configuration pour l'application SEO Keyword Analysis Tool
"""

import os
import json
import yaml
import getpass


def setup_config():
    print("Configuration de l'application SEO Keyword Analysis Tool")
    print("======================================================")
    print("Ce script va vous aider à configurer les fichiers nécessaires pour l'application.")

    # 1. Configuration Google Search Console
    print("\n1. Configuration Google Search Console")
    client_id = input("Client ID: ")
    client_secret = input("Client Secret: ")
    project_id = input("Project ID: ")

    # Créer client_secret.json
    client_secret_data = {
        "installed": {
            "client_id": client_id,
            "project_id": project_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost"]
        }
    }

    with open('client_secret.json', 'w') as f:
        json.dump(client_secret_data, f)

    print("✅ Fichier client_secret.json créé avec succès.")

    # 2. Configuration du site
    print("\n2. Configuration du site")
    site_url = input("URL du site dans Google Search Console (ex: https://www.exemple.com): ")

    # 3. Création du fichier config.yaml
    config_data = {
        'gsc': {
            'client_secret_file': 'client_secret.json',
            'token_file': 'token.json',
            'site_url': site_url
        },
        'directories': {
            'data': 'data',
            'output': 'data/output',
            'logs': 'data/logs'
        },
        'analysis': {
            'batch_size': 10,
            'max_results': 5000
        }
    }

    with open('config.yaml', 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False)

    print("✅ Fichier config.yaml créé avec succès.")

    # 4. Création des dossiers nécessaires
    os.makedirs('data/output', exist_ok=True)
    os.makedirs('data/logs', exist_ok=True)

    print("✅ Dossiers créés avec succès.")

    # 5. Configuration Streamlit (local)
    print("\n5. Configuration Streamlit local")

    app_password = getpass.getpass("Mot de passe pour accéder à l'application (laissez vide si pas nécessaire): ")

    streamlit_secrets = {
        'gsc': {
            'client_id': client_id,
            'client_secret': client_secret,
            'project_id': project_id
        },
        'site_url': site_url
    }

    if app_password:
        streamlit_secrets['app_password'] = app_password

    os.makedirs('.streamlit', exist_ok=True)

    with open('.streamlit/secrets.toml', 'w') as f:
        f.write('[gsc]\n')
        f.write(f'client_id = "{client_id}"\n')
        f.write(f'client_secret = "{client_secret}"\n')
        f.write(f'project_id = "{project_id}"\n')
        f.write(f'site_url = "{site_url}"\n')

        if app_password:
            f.write(f'app_password = "{app_password}"\n')

    print("✅ Fichier .streamlit/secrets.toml créé avec succès.")

    print("\nConfiguration terminée. Vous pouvez maintenant lancer l'application avec la commande:")
    print("streamlit run app.py")
    print(
        "\nNote: Vous devrez encore autoriser l'application à accéder à Google Search Console lors de la première exécution.")


if __name__ == "__main__":
    setup_config()