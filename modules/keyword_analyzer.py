import pandas as pd
import os
import math
from collections import Counter


class KeywordAnalyzer:
    """
    Classe pour l'analyse des mots-clés à partir des données GSC.
    """

    def __init__(self, gsc_manager, logger=None):
        """
        Initialise l'analyseur de mots-clés.

        Args:
            gsc_manager (GSCManager): Gestionnaire pour l'API Google Search Console
            logger (Logger, optional): Logger pour journaliser les opérations
        """
        self.gsc_manager = gsc_manager
        self.logger = logger

    def analyze_keywords(self, csv_file_path, site_url, start_date, end_date, batch_size=10, output_dir=None,
                         progress_callback=None):
        """
        Analyse les mots-clés à partir d'un fichier CSV et des données GSC.

        Args:
            csv_file_path (str): Chemin vers le fichier CSV contenant les mots-clés et URLs
            site_url (str): URL du site dans GSC
            start_date (str): Date de début au format YYYY-MM-DD
            end_date (str): Date de fin au format YYYY-MM-DD
            batch_size (int): Taille du lot de mots-clés à traiter en une fois
            output_dir (str): Répertoire de sortie pour les résultats. Si None, utilise le dossier 'output'
            progress_callback (callable): Fonction de callback pour suivre la progression

        Returns:
            str: Chemin vers le fichier de résultats
        """
        # Définir le chemin de sortie
        if output_dir is None:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(script_dir, 'data', 'output')

        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'SEO-Opportunities.xlsx')

        # Fichier de sauvegarde intermédiaire
        interim_file = os.path.join(output_dir, 'SEO-Opportunities-interim.xlsx')

        if self.logger:
            self.logger.info(f"Début de l'analyse des mots-clés depuis le fichier {csv_file_path}")
            self.logger.info(f"Les résultats seront sauvegardés dans {output_file}")

        # Lire le fichier CSV avec les mots-clés et URLs
        df_keywords = pd.read_csv(csv_file_path)

        if self.logger:
            self.logger.info(f"{len(df_keywords)} mots-clés trouvés dans le fichier")

        # Convertir les mots-clés en minuscules
        df_keywords['palabra clave'] = df_keywords['palabra clave'].str.lower()

        # Créer une liste pour stocker les résultats
        results = []

        # Vérifier s'il existe déjà des résultats intermédiaires
        processed_keywords = set()
        if os.path.exists(interim_file):
            try:
                existing_results = pd.read_excel(interim_file)
                # Récupérer les mots-clés déjà traités
                processed_keywords = set(existing_results['palabra clave'].str.lower())
                # Ajouter les résultats existants
                results = existing_results.to_dict('records')

                if self.logger:
                    self.logger.info(f"Reprise du traitement : {len(processed_keywords)} mots-clés déjà traités")

                # Filtrer les mots-clés non traités
                df_keywords = df_keywords[~df_keywords['palabra clave'].str.lower().isin(processed_keywords)]

                if self.logger:
                    self.logger.info(f"{len(df_keywords)} mots-clés restants à traiter")

            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Impossible de récupérer les résultats intermédiaires : {e}")

        # Calculer le nombre total de mots-clés et de lots
        total_keywords = len(df_keywords)
        num_batches = math.ceil(total_keywords / batch_size)

        if self.logger:
            self.logger.info(f"Traitement en {num_batches} lots de {batch_size} mots-clés maximum")

        # Traiter les mots-clés par lots
        for batch_index in range(num_batches):
            start_index = batch_index * batch_size
            end_index = min(start_index + batch_size, total_keywords)

            message = f"Analyse du lot {batch_index + 1}/{num_batches}: Mots-clés {start_index + 1} à {end_index}"
            if self.logger:
                self.logger.info(message)

            if progress_callback:
                progress_callback(batch_index, num_batches, message)

            # Extraire le lot de mots-clés
            batch_keywords = df_keywords['palabra clave'][start_index:end_index].tolist()

            # Obtenir les données GSC pour le lot
            gsc_data = self.gsc_manager.get_data_for_keywords(site_url, start_date, end_date, batch_keywords)

            # Convertir les données en DataFrame
            columns = ['page', 'query', 'clicks', 'impressions', 'position', 'ctr']
            df_gsc = pd.DataFrame(gsc_data, columns=columns)

            if self.logger:
                self.logger.info(f"Données GSC récupérées pour le lot. {len(df_gsc)} entrées.")

            # Traiter chaque mot-clé du lot
            for keyword_index in range(len(batch_keywords)):
                current_index = start_index + keyword_index
                keyword = df_keywords['palabra clave'].iloc[current_index]
                target_url = df_keywords['url'].iloc[current_index] if pd.notna(
                    df_keywords['url'].iloc[current_index]) else None

                if self.logger:
                    self.logger.info(f"Analyse du mot-clé {current_index + 1}/{total_keywords}: '{keyword}'")

                # Filtrer les données GSC pour ce mot-clé
                df_gsc_keyword = df_gsc[df_gsc['query'] == keyword]

                if not df_gsc_keyword.empty:
                    # Trouver la page avec le plus de clics ou d'impressions
                    if df_gsc_keyword['clicks'].max() > 0:
                        top_page = df_gsc_keyword.loc[df_gsc_keyword['clicks'].idxmax()]
                    else:
                        top_page = df_gsc_keyword.loc[df_gsc_keyword['impressions'].idxmax()]

                    if self.logger:
                        self.logger.info(f"URL trouvée dans GSC: {top_page['page']}")
                        self.logger.info(f"URL cible fournie: {target_url}")

                    # Déterminer si le mot-clé est bien positionné
                    if target_url:
                        if target_url == top_page['page']:
                            is_positioned = 'Yes'
                            if self.logger:
                                self.logger.info("Status: Yes - Le mot-clé est positionné sur l'URL cible")
                        else:
                            is_positioned = 'Yes with wrong page'
                            if self.logger:
                                self.logger.info(
                                    "Status: Yes with wrong page - Le mot-clé est positionné mais sur une URL différente")
                    else:
                        is_positioned = 'Yes with wrong page'
                        if self.logger:
                            self.logger.info(
                                "Status: Yes with wrong page - Le mot-clé est positionné mais pas d'URL cible spécifiée")

                    # Ajouter les résultats
                    results.append({
                        'url': target_url,
                        'palabra clave': keyword,
                        'clicks': top_page['clicks'],
                        'impressions': top_page['impressions'],
                        'position': top_page['position'],
                        'ctr': top_page['ctr'],
                        'top_page': top_page['page'],
                        'is_positioned': is_positioned
                    })

                    if self.logger:
                        self.logger.info(
                            f"Métriques - Clics: {top_page['clicks']}, Impressions: {top_page['impressions']}, Position: {top_page['position']}")
                else:
                    # Le mot-clé n'a pas de données dans GSC
                    results.append({
                        'url': target_url,
                        'palabra clave': keyword,
                        'clicks': 0,
                        'impressions': 0,
                        'position': None,
                        'ctr': 0,
                        'top_page': None,
                        'is_positioned': 'No'
                    })
                    if self.logger:
                        self.logger.info("Status: No - Le mot-clé n'est pas positionné")

                # Mise à jour de la progression pour chaque mot-clé
                if progress_callback:
                    overall_progress = batch_index * batch_size + keyword_index + 1
                    progress_callback(overall_progress, total_keywords, f"Analyse du mot-clé: '{keyword}'")

            # Après le traitement de chaque lot, sauvegarder les résultats intermédiaires
            interim_df = pd.DataFrame(results)
            interim_df.to_excel(interim_file, index=False)

            if self.logger:
                total_processed = len(results)
                total_to_process = total_keywords + len(processed_keywords)
                self.logger.info(
                    f"Sauvegarde intermédiaire effectuée : {total_processed}/{total_to_process} mots-clés traités.")

            if self.logger:
                self.logger.info(f"Lot {batch_index + 1}/{num_batches} terminé")

        if self.logger:
            self.logger.info("Analyse terminée. Préparation des résultats...")

        # Créer un DataFrame avec les résultats
        df_results = pd.DataFrame(results)

        # Sauvegarder les résultats dans un fichier Excel
        df_results.to_excel(output_file, index=False)

        # Supprimer le fichier intermédiaire
        if os.path.exists(interim_file):
            try:
                os.remove(interim_file)
                if self.logger:
                    self.logger.info(f"Fichier intermédiaire supprimé : {interim_file}")
            except:
                if self.logger:
                    self.logger.warning(f"Impossible de supprimer le fichier intermédiaire : {interim_file}")

        if self.logger:
            self.logger.info(f"Résultats sauvegardés dans {output_file}")

            # Statistiques récapitulatives
            positioned_count = len(df_results[df_results['is_positioned'] == 'Yes'])
            wrong_page_count = len(df_results[df_results['is_positioned'] == 'Yes with wrong page'])
            not_positioned_count = len(df_results[df_results['is_positioned'] == 'No'])

            self.logger.info(
                f"Récapitulatif: {positioned_count} bien positionnés, {wrong_page_count} mal positionnés, {not_positioned_count} non positionnés")

        return output_file

    def extract_frequent_ngrams(self, keywords, min_count=2):
        """
        Extrait les n-grams fréquents d'une liste de mots-clés.

        Args:
            keywords (list): Liste de mots-clés
            min_count (int): Nombre minimum d'occurrences pour considérer un n-gram comme fréquent

        Returns:
            list: Liste des n-grams fréquents
        """
        ngrams = Counter()

        for keyword in keywords:
            words = keyword.split()
            ngrams.update(words)

        frequent_ngrams = [ngram for ngram, count in ngrams.items() if count > min_count]
        return frequent_ngrams