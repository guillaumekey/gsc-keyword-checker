import os
import json
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import time


class GSCManager:
    """
    Gestionnaire pour l'API Google Search Console.
    Gère l'authentification et les requêtes à l'API.
    """

    # Scopes requis pour l'API
    SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

    def __init__(self, client_secret_file, token_file, logger=None):
        """
        Initialise le gestionnaire GSC.

        Args:
            client_secret_file (str): Chemin vers le fichier client_secret.json
            token_file (str): Chemin vers le fichier token.json
            logger (Logger, optional): Logger pour journaliser les opérations
        """
        self.client_secret_file_path = client_secret_file
        self.token_file_path = token_file
        self.service = None
        self.logger = logger

        # Obtenir les fichiers de credentials (possiblement des fichiers temporaires)
        self.token_file, self.client_secret_file = self.get_gsc_credentials()

    def get_gsc_credentials(self):
        """
        Récupère les credentials GSC depuis les secrets Streamlit ou les variables d'environnement
        et crée les fichiers temporaires nécessaires.

        Returns:
            tuple: (token_file_path, client_secret_file_path)
        """
        # En environnement Streamlit Cloud
        if hasattr(st, 'secrets') and 'gsc' in st.secrets:
            try:
                client_id = st.secrets.gsc.client_id
                client_secret = st.secrets.gsc.client_secret
                refresh_token = st.secrets.gsc.get('refresh_token', '')
                token = st.secrets.gsc.get('token', '')
                project_id = st.secrets.gsc.get('project_id', '')

                if self.logger:
                    self.logger.info("Utilisation des secrets Streamlit pour les credentials GSC")

                # Créer un objet credentials à partir des secrets
                creds_data = {
                    "token": token,
                    "refresh_token": refresh_token,
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scopes": ["https://www.googleapis.com/auth/webmasters.readonly"],
                    "universe_domain": "googleapis.com"
                }

                # Stocker temporairement dans un fichier
                temp_token_file = os.path.join(os.path.dirname(self.token_file_path), 'temp_token.json')
                with open(temp_token_file, 'w') as f:
                    json.dump(creds_data, f)

                # Même chose pour client_secret
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

                temp_client_secret_file = os.path.join(os.path.dirname(self.client_secret_file_path),
                                                       'temp_client_secret.json')
                with open(temp_client_secret_file, 'w') as f:
                    json.dump(client_secret_data, f)

                if self.logger:
                    self.logger.info(f"Fichiers temporaires pour GSC créés à partir des secrets Streamlit")

                return temp_token_file, temp_client_secret_file
            except Exception as e:
                if self.logger:
                    self.logger.error(
                        f"Erreur lors de la création des fichiers de credentials à partir des secrets: {str(e)}")
                # Fallback aux fichiers locaux
                return self.token_file_path, self.client_secret_file_path

        # En environnement local avec variables d'environnement
        elif all(k in os.environ for k in ['GSC_CLIENT_ID', 'GSC_CLIENT_SECRET']):
            try:
                client_id = os.environ['GSC_CLIENT_ID']
                client_secret = os.environ['GSC_CLIENT_SECRET']
                refresh_token = os.environ.get('GSC_REFRESH_TOKEN', '')
                token = os.environ.get('GSC_TOKEN', '')
                project_id = os.environ.get('GSC_PROJECT_ID', '')

                if self.logger:
                    self.logger.info("Utilisation des variables d'environnement pour les credentials GSC")

                # Créer des fichiers JSON temporaires à partir des variables d'environnement
                creds_data = {
                    "token": token,
                    "refresh_token": refresh_token,
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scopes": ["https://www.googleapis.com/auth/webmasters.readonly"],
                    "universe_domain": "googleapis.com"
                }

                temp_token_file = os.path.join(os.path.dirname(self.token_file_path), 'temp_token.json')
                with open(temp_token_file, 'w') as f:
                    json.dump(creds_data, f)

                # Même chose pour client_secret
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

                temp_client_secret_file = os.path.join(os.path.dirname(self.client_secret_file_path),
                                                       'temp_client_secret.json')
                with open(temp_client_secret_file, 'w') as f:
                    json.dump(client_secret_data, f)

                if self.logger:
                    self.logger.info(f"Fichiers temporaires pour GSC créés à partir des variables d'environnement")

                return temp_token_file, temp_client_secret_file
            except Exception as e:
                if self.logger:
                    self.logger.error(
                        f"Erreur lors de la création des fichiers de credentials à partir des variables d'environnement: {str(e)}")
                # Fallback aux fichiers locaux
                return self.token_file_path, self.client_secret_file_path

        # Fallback aux fichiers locaux (pour le développement uniquement)
        else:
            if self.logger:
                self.logger.info(
                    f"Utilisation des fichiers de credentials locaux: {self.token_file_path}, {self.client_secret_file_path}")

            return self.token_file_path, self.client_secret_file_path

    def get_credentials(self):
        """
        Obtient les credentials OAuth2 pour l'API Google Search Console.

        Returns:
            Credentials: Object credentials pour l'API
        """
        creds = None

        if self.logger:
            self.logger.info("Vérification des credentials Google Search Console...")

        # Vérifier si un token existe déjà
        if os.path.exists(self.token_file):
            if self.logger:
                self.logger.info(f"Fichier token trouvé: {self.token_file}")
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        else:
            if self.logger:
                self.logger.info(f"Aucun fichier token trouvé à {self.token_file}")

        # Si pas de credentials valides, en obtenir de nouvelles
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                if self.logger:
                    self.logger.info("Token expiré, renouvellement...")
                try:
                    creds.refresh(Request())
                    if self.logger:
                        self.logger.info("Token renouvelé avec succès")

                    # Sauvegarder le token renouvelé
                    with open(self.token_file, 'w') as token:
                        token.write(creds.to_json())
                        if self.logger:
                            self.logger.info(f"Token renouvelé sauvegardé dans {self.token_file}")

                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Erreur lors du renouvellement du token: {str(e)}")
                    # Affichage d'un message d'erreur à l'utilisateur
                    if 'STREAMLIT_SHARING_MODE' in os.environ or hasattr(st, 'secrets'):
                        st.error(
                            "Le token d'accès a expiré. Veuillez contacter l'administrateur pour le mettre à jour.")
            else:
                # Authentification nécessaire
                if 'STREAMLIT_SHARING_MODE' in os.environ or (hasattr(st, 'secrets') and 'gsc' in st.secrets):
                    # En mode Streamlit Cloud, impossible d'ouvrir le flux d'authentification
                    if self.logger:
                        self.logger.error("Authentification requise mais impossible en mode Streamlit Cloud")
                    st.error(
                        "Erreur d'authentification. Veuillez contacter l'administrateur pour configurer l'accès à l'API.")
                    return None
                else:
                    # Flux d'authentification local
                    if self.logger:
                        self.logger.info("Lancement du flux d'authentification OAuth2...")
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, self.SCOPES)
                        creds = flow.run_local_server(port=0)
                        if self.logger:
                            self.logger.info("Authentification OAuth2 réussie")

                        # Sauvegarder le token pour la prochaine fois
                        with open(self.token_file, 'w') as token:
                            token.write(creds.to_json())
                            if self.logger:
                                self.logger.info(f"Token sauvegardé dans {self.token_file}")

                        # Mise à jour des environnements variables également (pour faciliter le développement)
                        credentials_json = json.loads(creds.to_json())
                        os.environ['GSC_TOKEN'] = credentials_json.get('token', '')
                        os.environ['GSC_REFRESH_TOKEN'] = credentials_json.get('refresh_token', '')
                    except Exception as e:
                        if self.logger:
                            self.logger.error(f"Erreur lors de l'authentification OAuth2: {str(e)}")
                        return None
        else:
            if self.logger:
                self.logger.info("Credentials valides trouvées")

        return creds

    def initialize_service(self):
        """
        Initialise le service Google Search Console.

        Returns:
            Resource: Service GSC initialisé
        """
        if self.service is None:
            creds = self.get_credentials()
            if creds:
                self.service = build('searchconsole', 'v1', credentials=creds)
            else:
                if self.logger:
                    self.logger.error("Impossible d'initialiser le service GSC: aucune credential valide")
                return None

        return self.service

    def get_data_for_keywords(self, site_url, start_date, end_date, keywords_batch, max_rows=5000):
        """
        Récupère les données GSC pour un lot de mots-clés.

        Args:
            site_url (str): URL du site dans GSC
            start_date (str): Date de début au format YYYY-MM-DD
            end_date (str): Date de fin au format YYYY-MM-DD
            keywords_batch (list): Liste des mots-clés à interroger
            max_rows (int): Nombre maximum de lignes à récupérer

        Returns:
            list: Liste des données pour chaque mot-clé
        """
        service = self.initialize_service()
        if not service:
            if self.logger:
                self.logger.error("Service GSC non initialisé. Impossible de récupérer les données.")
            return []

        data = []

        batch_size = len(keywords_batch)
        if self.logger:
            self.logger.info(f"Récupération des données pour un lot de {batch_size} mots-clés")
            self.logger.info(f"Période: {start_date} au {end_date}")

        for i, keyword in enumerate(keywords_batch):
            if self.logger:
                self.logger.info(f"Traitement du mot-clé {i + 1}/{batch_size}: '{keyword}'")

            # Ajouter une pause tous les 3 mots-clés pour éviter les limitations de l'API
            if i > 0 and i % 3 == 0:
                if self.logger:
                    self.logger.info(f"Pause de 1 seconde pour éviter les limitations de l'API...")
                time.sleep(1)  # Pause d'une seconde

            request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['page', 'query'],
                'dimensionFilterGroups': [{
                    'filters': [{
                        'dimension': 'query',
                        'operator': 'equals',
                        'expression': keyword
                    }]
                }],
                'rowLimit': max_rows
            }

            try:
                if self.logger:
                    self.logger.info(f"Envoi de la requête à l'API GSC pour '{keyword}'")

                # Tenter d'exécuter la requête, avec des tentatives en cas d'échec
                max_retries = 3
                retry_delay = 2  # secondes
                response = None

                for retry in range(max_retries):
                    try:
                        response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
                        break  # Sortir de la boucle si la requête réussit
                    except Exception as e:
                        if retry < max_retries - 1:  # Si ce n'est pas la dernière tentative
                            if self.logger:
                                self.logger.warning(
                                    f"Tentative {retry + 1} échouée pour '{keyword}': {e}. Nouvelle tentative dans {retry_delay} secondes...")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Augmenter le délai entre les tentatives
                        else:
                            # Dernière tentative a échoué
                            raise e

                if response:
                    rows = response.get('rows', [])

                    if not rows and self.logger:
                        self.logger.info(f"Aucune donnée trouvée pour le mot-clé '{keyword}'")
                    elif self.logger:
                        self.logger.info(f"{len(rows)} résultats trouvés pour le mot-clé '{keyword}'")

                    for row in rows:
                        keys = row['keys']
                        data.append([
                            keys[0],  # page
                            keys[1].lower(),  # query
                            row['clicks'],  # clicks
                            row['impressions'],  # impressions
                            row['position'],  # position
                            row['ctr']  # ctr (Click-Through Rate)
                        ])
            except Exception as e:
                error_msg = f"Erreur lors de la récupération des données pour le mot-clé '{keyword}': {e}"
                if self.logger:
                    self.logger.error(error_msg)
                else:
                    print(error_msg)

                # Continuer avec le mot-clé suivant au lieu d'arrêter tout le processus

        if self.logger:
            self.logger.info(f"Récupération terminée. {len(data)} entrées de données récupérées.")

        return data

    def get_top_keywords_for_page(self, site_url, start_date, end_date, page, limit=20):
        """
        Récupère les top mots-clés pour une page spécifique.

        Args:
            site_url (str): URL du site dans GSC
            start_date (str): Date de début au format YYYY-MM-DD
            end_date (str): Date de fin au format YYYY-MM-DD
            page (str): URL de la page
            limit (int): Nombre maximum de mots-clés à récupérer

        Returns:
            list: Liste des top mots-clés pour la page
        """
        service = self.initialize_service()
        if not service:
            if self.logger:
                self.logger.error("Service GSC non initialisé. Impossible de récupérer les top mots-clés.")
            return []

        request = {
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': ['query'],
            'dimensionFilterGroups': [{
                'filters': [{
                    'dimension': 'page',
                    'operator': 'equals',
                    'expression': page
                }]
            }],
            'rowLimit': limit,
            'startRow': 0,
            'orderBy': [{'field': 'clicks', 'descending': True}]
        }

        try:
            response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
            rows = response.get('rows', [])
            top_keywords = [row['keys'][0] for row in rows]
            return top_keywords
        except Exception as e:
            error_msg = f"Erreur lors de la récupération des top mots-clés pour la page '{page}': {e}"
            if self.logger:
                self.logger.error(error_msg)
            else:
                print(error_msg)
            return []

    def cleanup_temp_files(self):
        """
        Nettoie les fichiers temporaires créés pour les credentials.
        """
        try:
            temp_files = [
                os.path.join(os.path.dirname(self.token_file_path), 'temp_token.json'),
                os.path.join(os.path.dirname(self.client_secret_file_path), 'temp_client_secret.json')
            ]

            for file_path in temp_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    if self.logger:
                        self.logger.info(f"Fichier temporaire supprimé: {file_path}")
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Erreur lors du nettoyage des fichiers temporaires: {str(e)}")