import os
import yaml
import streamlit as st


def setup_directories(directories):
    """
    Crée les répertoires nécessaires pour l'application.

    Args:
        directories (dict): Dictionnaire des répertoires à créer
    """
    for dir_name, dir_path in directories.items():
        os.makedirs(dir_path, exist_ok=True)
        print(f"Répertoire créé/vérifié: {dir_path}")


def load_config(config_file=None):
    """
    Charge la configuration depuis les secrets Streamlit, un fichier YAML ou crée une configuration par défaut.

    Args:
        config_file (str): Chemin vers le fichier de configuration

    Returns:
        dict: Configuration chargée
    """
    # URL du site par défaut (domaine exemple non-existant)
    default_site_url = "https://www.exemple-site.com"

    # Priorité aux secrets Streamlit
    if hasattr(st, 'secrets'):
        # Récupérer l'URL du site depuis les secrets
        site_url = st.secrets.get('site_url', default_site_url)

        # Créer la configuration
        config = {
            'gsc': {
                'client_secret_file': 'client_secret.json',  # Ces fichiers seront générés temporairement
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

        print("Configuration chargée depuis les secrets Streamlit")
        return config

    # Vérifier les variables d'environnement
    elif 'GSC_SITE_URL' in os.environ:
        site_url = os.environ.get('GSC_SITE_URL', default_site_url)

        # Créer la configuration
        config = {
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

        print("Configuration chargée depuis les variables d'environnement")
        return config

    # Chemin par défaut pour la configuration
    if config_file is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_file = os.path.join(root_dir, 'config.yaml')

    # Si le fichier de configuration existe, le charger
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        print(f"Configuration chargée depuis {config_file}")
    else:
        # Créer une configuration par défaut
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config = {
            'gsc': {
                'client_secret_file': os.path.join(root_dir, 'client_secret.json'),
                'token_file': os.path.join(root_dir, 'token.json'),
                'site_url': default_site_url
            },
            'directories': {
                'data': os.path.join(root_dir, 'data'),
                'output': os.path.join(root_dir, 'data', 'output'),
                'logs': os.path.join(root_dir, 'data', 'logs')
            },
            'analysis': {
                'batch_size': 10,
                'max_results': 5000
            }
        }

        # Sauvegarder la configuration par défaut
        try:
            with open(config_file, 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False)
            print(f"Configuration par défaut créée et sauvegardée dans {config_file}")
        except Exception as e:
            print(f"Impossible de sauvegarder la configuration: {str(e)}")

    return config


def get_version():
    """
    Renvoie la version actuelle de l'application.

    Returns:
        str: Version de l'application
    """
    return "1.0.0"


def get_file_size(file_path):
    """
    Renvoie la taille d'un fichier en Mo.

    Args:
        file_path (str): Chemin vers le fichier

    Returns:
        float: Taille du fichier en Mo
    """
    if os.path.exists(file_path):
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 2)
    return 0