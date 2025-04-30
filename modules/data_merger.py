import pandas as pd
import os
import re


class DataMerger:
    """
    Classe pour fusionner les données d'analyse SEO et de crawl.
    """

    def __init__(self, logger=None):
        """
        Initialise le fusionneur de données.

        Args:
            logger (Logger, optional): Logger pour journaliser les opérations
        """
        self.logger = logger

    def merge_data(self, seo_file, crawl_file=None, columns_to_check=None, output_dir=None, progress_callback=None):
        """
        Fusionne les données d'analyse SEO et de crawl.

        Args:
            seo_file (str): Chemin vers le fichier d'analyse SEO
            crawl_file (str): Chemin vers le fichier de crawl traité (optionnel)
            columns_to_check (list): Liste des colonnes à vérifier pour la présence de mots-clés
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
        output_file = os.path.join(output_dir, 'Final-SEO-Opportunities.xlsx')

        # Charger les résultats de SEO Opportunities
        if self.logger:
            self.logger.info(f"Chargement du fichier d'analyse SEO: {seo_file}")

        if progress_callback:
            progress_callback(1, 5, "Chargement du fichier d'analyse SEO...")

        df_seo = pd.read_excel(seo_file)

        if self.logger:
            self.logger.info(f"Fichier d'analyse SEO chargé avec succès. {len(df_seo)} mots-clés trouvés.")

        # Si pas de fichier de crawl, retourner simplement le fichier SEO
        if crawl_file is None or not os.path.exists(crawl_file):
            if self.logger:
                self.logger.warning("Pas de fichier de crawl fourni. Retour des résultats d'analyse SEO uniquement.")

            df_seo.to_excel(output_file, index=False)

            if self.logger:
                self.logger.info(f"Résultats sauvegardés dans {output_file}")

            return output_file

def _generate_variants(self, keyword):
    """
    Génère différentes variantes d'un mot-clé.

    Args:
        keyword (str): Mot-clé à varier

    Returns:
        set: Ensemble des variantes du mot-clé
    """
    # Stop words multilingues
    stop_words = {
        # Français
        'à', 'de', 'des', 'du', 'et', 'en', 'au', 'aux', 'avec', 'dans', 'par', 'pour', 'sur',
        'les', 'la', 'le', 'un', 'une', 'des', 'ce', 'ces', 'sa', 'ses', 'son',

        # Anglais
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in',
        'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will', 'with',

        # Espagnol
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'y', 'o', 'pero', 'si',
        'de', 'del', 'al', 'a', 'ante', 'bajo', 'con', 'contra', 'desde', 'en',
        'entre', 'hacia', 'hasta', 'para', 'por', 'según', 'sin', 'sobre', 'tras'
    }

    # Liste des séparateurs courants dans les titres web
    separators = {'-', '|', ':', '>', '»', '/', '•', '·', '–', '—', '_'}

    keyword = keyword.lower()
    variants = set()

    # Fonction pour nettoyer le texte des séparateurs
    def clean_text(text):
        # Remplacer les séparateurs par des espaces
        for sep in separators:
            text = text.replace(sep, ' ')
        # Normaliser les espaces multiples
        return re.sub(r'\s+', ' ', text.strip())

    # Ajouter les variantes de base
    variants.add(keyword)
    variants.add(clean_text(keyword))
    variants.add(''.join(keyword.split()))

    # Pour chaque séparateur, créer des variantes
    words = keyword.split()
    for sep in separators:
        variants.add(sep.join(words))

    # Ajouter les variantes au pluriel
    variants.add(keyword + "s")
    variants.add(clean_text(keyword) + "s")
    variants.add(''.join(keyword.split()) + "s")

    # Gestion des formes avec stop words
    if len(words) >= 2:
        for i in range(len(words) - 1):
            for stop_word in stop_words:
                words_with_stop = words.copy()
                words_with_stop.insert(i + 1, stop_word)
                base_variant = ' '.join(words_with_stop)
                variants.add(base_variant)
                for sep in separators:
                    variants.add(sep.join(words_with_stop))

        # Variante sans stop words (mots collés)
        clean_words = [word for word in words if word not in stop_words]
        variants.add(' '.join(clean_words))
        for sep in separators:
            variants.add(sep.join(clean_words))
        variants.add(''.join(clean_words))

    # Gestion des pluriels spéciaux
    if keyword.endswith('y'):
        base = keyword[:-1] + 'ies'
        variants.add(base)
        variants.add(clean_text(base))
        variants.add(''.join(base.split()))
    elif keyword.endswith('s'):
        base = keyword + 'es'
        variants.add(base)
        variants.add(clean_text(base))
        variants.add(''.join(base.split()))
    elif keyword.endswith('z'):
        base = keyword[:-1] + 'ces'
        variants.add(base)
        variants.add(clean_text(base))
        variants.add(''.join(base.split()))
    elif keyword.endswith('ón'):
        base = keyword[:-2] + 'ones'
        variants.add(base)
        variants.add(clean_text(base))
        variants.add(''.join(base.split()))

    return variants


def _clean_text_for_comparison(self, text):
    """
    Nettoie le texte pour la comparaison avec les mots-clés.

    Args:
        text (str): Texte à nettoyer

    Returns:
        str: Texte nettoyé
    """
    # Liste des caractères à traiter comme des espaces
    separators = {'-', '|', ':', '>', '»', '/', '•', '·', '–', '—', '_'}

    # Remplacer les séparateurs par des espaces
    for sep in separators:
        text = text.replace(sep, ' ')

    # Normaliser les espaces multiples et les espaces en début/fin
    return re.sub(r'\s+', ' ', text.strip())


def _check_keyword_presence(self, row, column_name):
    """
    Vérifie la présence du mot-clé dans le texte.

    Args:
        row (Series): Ligne du DataFrame
        column_name (str): Nom de la colonne à vérifier

    Returns:
        str: 'Sí' si le mot-clé est présent, 'No' sinon
    """
    keyword = str(row['palabra clave']).lower()
    keyword_variants = self._generate_variants(keyword)

    if column_name == 'all_desc':
        # Vérifier dans toutes les colonnes all_desc_X
        for i in range(1, 5):  # Vérifie all_desc_1 à all_desc_4
            col = f'all_desc_{i}'
            if col in row.index:
                text = str(row[col]).lower()
                if pd.isna(text) or text == 'nan' or text == '':
                    continue

                cleaned_text = self._clean_text_for_comparison(text)

                for kw in keyword_variants:
                    # Pattern plus flexible
                    pattern = r'(?:^|\b|\s|[-|:>»/•·–—_])' + re.escape(kw) + r'(?:$|\b|\s|[-|:>»/•·–—_])'
                    if re.search(pattern, text, re.IGNORECASE) or re.search(pattern, cleaned_text, re.IGNORECASE):
                        return 'Sí'
        return 'No'
    else:
        # Pour les autres colonnes
        text = str(row[column_name]).lower()
        if pd.isna(text) or text == 'nan' or text == '':
            return 'No'

        cleaned_text = self._clean_text_for_comparison(text)

        for kw in keyword_variants:
            pattern = r'(?:^|\b|\s|[-|:>»/•·–—_])' + re.escape(kw) + r'(?:$|\b|\s|[-|:>»/•·–—_])'
            if re.search(pattern, text, re.IGNORECASE) or re.search(pattern, cleaned_text, re.IGNORECASE):
                return 'Sí'
        return 'No'