import logging
import os
import datetime
import streamlit as st


class Logger:
    """
    Classe pour gérer les logs de l'application.
    Permet de journaliser à la fois dans un fichier et dans l'interface Streamlit.
    """

    def __init__(self, log_dir=None, level=logging.INFO):
        """
        Initialise le logger.

        Args:
            log_dir (str): Répertoire où stocker les fichiers de log
            level (int): Niveau de logging (INFO, DEBUG, etc.)
        """
        self.logger = logging.getLogger('seo_tool')
        self.logger.setLevel(level)
        self.logger.handlers = []  # Clear any existing handlers

        # Format de log détaillé
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Logger vers un fichier
        if log_dir is None:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')

        os.makedirs(log_dir, exist_ok=True)

        # Nom du fichier de log avec date et heure
        log_filename = f"seo_tool_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = os.path.join(log_dir, log_filename)

        # Configurer le handler de fichier
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        self.logger.addHandler(file_handler)

        # Enregistrer le chemin du fichier de log
        self.log_path = log_path

        self.info(f"Logger initialisé. Fichier de log: {log_path}")

    def info(self, message):
        """
        Enregistre un message de niveau INFO.

        Args:
            message (str): Message à journaliser
        """
        self.logger.info(message)
        self._log_to_streamlit("INFO", message)

    def warning(self, message):
        """
        Enregistre un message de niveau WARNING.

        Args:
            message (str): Message à journaliser
        """
        self.logger.warning(message)
        self._log_to_streamlit("WARNING", message)

    def error(self, message):
        """
        Enregistre un message de niveau ERROR.

        Args:
            message (str): Message à journaliser
        """
        self.logger.error(message)
        self._log_to_streamlit("ERROR", message, is_error=True)

    def debug(self, message):
        """
        Enregistre un message de niveau DEBUG.

        Args:
            message (str): Message à journaliser
        """
        self.logger.debug(message)
        # Ne pas afficher les messages DEBUG dans Streamlit par défaut

    def _log_to_streamlit(self, level, message, is_error=False):
        """
        Affiche un message de log dans l'interface Streamlit si disponible.

        Args:
            level (str): Niveau de log (INFO, WARNING, etc.)
            message (str): Message à afficher
            is_error (bool): True si c'est une erreur (affichage spécial)
        """
        try:
            # Utiliser directement les fonctions de Streamlit sans conteneur
            if is_error:
                st.error(f"{level}: {message}")
            elif level == "WARNING":
                st.warning(message)
            else:
                st.info(message)
        except:
            # Si Streamlit n'est pas disponible ou en cas d'erreur, ignorer silencieusement
            pass

    def get_log_path(self):
        """
        Renvoie le chemin du fichier de log actuel.

        Returns:
            str: Chemin du fichier de log
        """
        return self.log_path

    def create_log_container(self):
        """
        Crée un conteneur Streamlit pour les logs.
        Ce conteneur est enregistré dans session_state pour être accessible globalement.

        Returns:
            streamlit.container: Conteneur pour les logs
        """
        # Au lieu d'utiliser un conteneur stocké dans session_state
        # Créer un simple expander à chaque fois
        return st.empty()