import pandas as pd
import os
import re


class CrawlProcessor:
    """
    Classe pour traiter les données de crawl d'un site web.
    """

    def __init__(self, logger=None):
        """
        Initialise le processeur de données de crawl.

        Args:
            logger (Logger, optional): Logger pour journaliser les opérations
        """
        self.logger = logger

    def process_crawl_data(self, crawl_file_path, output_dir=None, progress_callback=None):
        """
        Traite les données de crawl depuis un fichier CSV.

        Args:
            crawl_file_path (str): Chemin vers le fichier CSV de crawl
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
        output_file = os.path.join(output_dir, 'crawl-client-updated.xlsx')

        # Lire le fichier CSV de crawl
        if self.logger:
            self.logger.info(f"Lecture du fichier CSV de crawl: {crawl_file_path}")

        df_crawl = pd.read_csv(crawl_file_path, encoding='utf-8', low_memory=False)

        if self.logger:
            self.logger.info(f"Fichier chargé avec succès. {len(df_crawl)} URLs trouvées.")
            self.logger.info(f"Colonnes disponibles: {', '.join(df_crawl.columns[:10])}...")

        # Convertir les noms de colonnes en minuscules
        df_crawl.columns = df_crawl.columns.str.lower()

        # Traiter les descriptions
        if self.logger:
            self.logger.info("Traitement des descriptions...")

        if progress_callback:
            progress_callback(1, 3, "Traitement des descriptions...")

        self._process_descriptions(df_crawl, progress_callback)

        # Traiter les H2
        if self.logger:
            self.logger.info("Traitement des H2...")

        if progress_callback:
            progress_callback(2, 3, "Traitement des H2...")

        self._process_h2(df_crawl)

        # Sauvegarder le DataFrame traité
        if self.logger:
            self.logger.info(f"Sauvegarde du fichier traité dans {output_file}")

        if progress_callback:
            progress_callback(3, 3, "Sauvegarde du fichier...")

        df_crawl.to_excel(output_file, index=False)

        if self.logger:
            self.logger.info("Traitement du fichier de crawl terminé avec succès")

        return output_file

    def _clean_text(self, text):
        """
        Nettoie le texte des caractères spéciaux et espaces multiples.

        Args:
            text (str): Texte à nettoyer

        Returns:
            str: Texte nettoyé
        """
        if not isinstance(text, str):
            return ""

        # Nettoyer les espaces multiples
        text = re.sub(r'\s+', ' ', text.strip())

        # Supprimer les caractères non-imprimables
        text = ''.join(char for char in text if char.isprintable())

        return text

    def _split_text_into_chunks(self, text, max_length=20000):
        """
        Divise le texte en morceaux plus petits à des points logiques.

        Args:
            text (str): Texte à diviser
            max_length (int): Longueur maximale de chaque morceau

        Returns:
            list: Liste des morceaux de texte
        """
        text = self._clean_text(text)
        chunks = []

        while text:
            if len(text) <= max_length:
                chunks.append(text)
                break

            # Chercher un point de coupure logique
            cut_point = max_length
            for separator in ['. ', '! ', '? ', '; ', ', ', ' ']:
                last_sep = text[:max_length].rfind(separator)
                if last_sep != -1:
                    cut_point = last_sep + 1
                    break

            chunks.append(text[:cut_point].strip())
            text = text[cut_point:].strip()

        return chunks

    def _process_descriptions(self, df_crawl, progress_callback=None):
        """
        Traite les descriptions du crawl.

        Args:
            df_crawl (DataFrame): DataFrame contenant les données de crawl
            progress_callback (callable): Fonction de callback pour suivre la progression
        """
        # Initialiser les colonnes pour le texte divisé
        all_desc_columns = ['all_desc_1', 'all_desc_2', 'all_desc_3', 'all_desc_4']
        for col in all_desc_columns:
            df_crawl[col] = ''

        # Identifier les colonnes de description
        bottom_desc_cols = [col for col in df_crawl.columns if col.startswith('bottom description')]

        if self.logger:
            self.logger.info(f"Traitement des descriptions pour {len(df_crawl)} URLs")
            self.logger.info(f"{len(bottom_desc_cols)} colonnes de description trouvées")

        # Traiter chaque ligne
        total_rows = len(df_crawl)
        for idx, row_idx in enumerate(df_crawl.index):
            if idx % 100 == 0 and self.logger:
                self.logger.info(
                    f"Traitement des descriptions: {idx}/{total_rows} URLs traitées ({idx / total_rows * 100:.1f}%)")

            if progress_callback and idx % 10 == 0:
                progress_callback(idx, total_rows, f"Traitement des descriptions: {idx}/{total_rows} URLs")

            full_desc = ""

            # Concatener toutes les descriptions
            for col_name in bottom_desc_cols:
                value = df_crawl.at[row_idx, col_name]
                if pd.notna(value):
                    full_desc += " " + str(value)

            # Nettoyer et diviser le texte
            chunks = self._split_text_into_chunks(full_desc)

            # Sauvegarder les morceaux dans les colonnes
            for i, chunk in enumerate(chunks[:4]):  # Limiter à 4 colonnes
                df_crawl.at[row_idx, all_desc_columns[i]] = chunk

        # Supprimer les anciennes colonnes de description
        if self.logger:
            self.logger.info(f"Suppression des {len(bottom_desc_cols)} colonnes de description originales")

        df_crawl.drop(columns=bottom_desc_cols, inplace=True, errors='ignore')

        if self.logger:
            self.logger.info("Traitement des descriptions terminé avec succès")

    def _process_h2(self, df_crawl):
        """
        Traite les titres H2 du crawl.

        Args:
            df_crawl (DataFrame): DataFrame contenant les données de crawl
        """
        # Initialiser la colonne pour tous les H2
        df_crawl['all_h2list'] = ''

        # Identifier les colonnes H2
        h2_cols = [col for col in df_crawl.columns if col.startswith('h2 ')]

        if self.logger:
            self.logger.info(f"Traitement des H2 pour {len(df_crawl)} URLs")
            self.logger.info(f"{len(h2_cols)} colonnes H2 trouvées")

        # Concatener tous les H2
        for col_name in h2_cols:
            df_crawl['all_h2list'] += df_crawl[col_name].fillna('').astype(str) + ' '

        # Nettoyer all_h2list
        if self.logger:
            self.logger.info("Nettoyage des H2 concaténés")

        df_crawl['all_h2list'] = df_crawl['all_h2list'].apply(self._clean_text)

        # Supprimer les anciennes colonnes H2
        if self.logger:
            self.logger.info(f"Suppression des {len(h2_cols)} colonnes H2 originales")

        df_crawl.drop(columns=h2_cols, inplace=True, errors='ignore')

        if self.logger:
            self.logger.info("Traitement des H2 terminé avec succès")