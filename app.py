"""
Application principale pour l'analyse SEO des mots-clés

Cette application permet d'analyser le positionnement des mots-clés dans
Google Search Console et de vérifier leur présence dans différents éléments
des pages web à partir d'un fichier de crawl.
"""

import streamlit as st
import pandas as pd
import os
import datetime

from modules.utils import setup_directories, load_config
from modules.logger import Logger
from pages import keywords_page, crawl_page, merger_page, results_page


def check_password():
    """Retourne True si le mot de passe est correct, sinon False."""
    if hasattr(st, 'secrets') and 'app_password' in st.secrets:
        expected_password = st.secrets["app_password"]

        def password_entered():
            if st.session_state["password"] == expected_password:
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Ne pas garder le mot de passe en mémoire
            else:
                st.session_state["password_correct"] = False

        if "password_correct" not in st.session_state:
            # Premier chargement, afficher l'input du mot de passe
            st.text_input(
                "Mot de passe", type="password", on_change=password_entered, key="password"
            )
            return False
        elif not st.session_state["password_correct"]:
            # Mot de passe incorrect, afficher l'input à nouveau
            st.text_input(
                "Mot de passe", type="password", on_change=password_entered, key="password"
            )
            st.error("😕 Mot de passe incorrect")
            return False
        else:
            # Mot de passe correct
            return True
    else:
        # Pas de protection par mot de passe configurée
        return True


def main():
    """
    Point d'entrée principal de l'application.
    Configure l'interface et gère la navigation entre les pages.
    """
    # Configuration de la page
    st.set_page_config(
        page_title="SEO Keyword Analysis Tool",
        page_icon="🔍",
        layout="wide"
    )

    # Vérifier le mot de passe si configuré
    if not check_password():
        st.stop()  # Arrêter l'exécution si le mot de passe est incorrect

    # Charger la configuration
    config = load_config()
    setup_directories(config['directories'])

    # Initialiser le logger
    if 'logger' not in st.session_state:
        log_dir = os.path.join(config['directories']['data'], 'logs')
        st.session_state.logger = Logger(log_dir=log_dir)

    # Créer un conteneur pour les logs
    st.session_state.logger.create_log_container()

    # Header
    st.title("SEO Keyword Analysis Tool")
    st.markdown(
        "*Un outil pour analyser le positionnement de vos mots-clés et identifier les opportunités d'optimisation SEO*")

    # Sidebar pour la navigation
    with st.sidebar:
        st.header("Configuration")

        # Configuration de l'API
        st.subheader("Google Search Console")
        site_url = st.text_input("URL du site", value=config['gsc']['site_url'])

        # Sélection des dates
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Date de début",
                value=datetime.datetime.now() - datetime.timedelta(days=30)
            )
        with col2:
            end_date = st.date_input(
                "Date de fin",
                value=datetime.datetime.now()
            )

        # Navigation
        st.subheader("Navigation")
        page = st.radio(
            "Sélectionnez une option",
            ["Analyse de mots-clés", "Traitement de crawl", "Fusion des données", "Résultats"]
        )

        # État de la session
        st.divider()
        st.subheader("État de la session")

        # Afficher les données en mémoire
        session_items = []
        if 'df_keywords' in st.session_state:
            keywords_count = len(st.session_state['df_keywords'])
            session_items.append(f"✅ Mots-clés: {keywords_count} chargés")
        else:
            session_items.append("❌ Mots-clés: non chargés")

        if 'df_crawl' in st.session_state:
            crawl_count = len(st.session_state['df_crawl'])
            session_items.append(f"✅ Crawl: {crawl_count} URLs chargées")
        else:
            session_items.append("❌ Crawl: non chargé")

        if 'keywords_results_path' in st.session_state:
            session_items.append("✅ Résultats SEO: disponibles")
        else:
            session_items.append("❌ Résultats SEO: non disponibles")

        if 'crawl_results_path' in st.session_state:
            session_items.append("✅ Résultats crawl: disponibles")
        else:
            session_items.append("❌ Résultats crawl: non disponibles")

        if 'merge_results_path' in st.session_state:
            session_items.append("✅ Fusion: disponible")
        else:
            session_items.append("❌ Fusion: non disponible")

        # Afficher l'état
        for item in session_items:
            st.markdown(item)

        # Bouton pour réinitialiser la session
        if st.button("Réinitialiser toutes les données"):
            # Sauvegarder le logger
            logger = st.session_state.get('logger')

            # Effacer toutes les clés sauf logger
            for key in list(st.session_state.keys()):
                if key != 'logger':
                    del st.session_state[key]

            # Restaurer le logger
            if logger:
                st.session_state['logger'] = logger
                logger.info("Toutes les données ont été réinitialisées")

            st.success("Toutes les données ont été réinitialisées")
            st.rerun()

        # Afficher le chemin du fichier de log
        if 'logger' in st.session_state:
            st.info(f"Logs: {os.path.basename(st.session_state.logger.get_log_path())}")

            # Bouton pour télécharger les logs
            with open(st.session_state.logger.get_log_path(), 'r') as log_file:
                st.download_button(
                    label="Télécharger les logs",
                    data=log_file,
                    file_name=os.path.basename(st.session_state.logger.get_log_path()),
                    mime="text/plain"
                )

    # Afficher la page sélectionnée
    if page == "Analyse de mots-clés":
        keywords_page(config, site_url, start_date, end_date)
    elif page == "Traitement de crawl":
        crawl_page(config)
    elif page == "Fusion des données":
        merger_page(config)
    elif page == "Résultats":
        results_page(config)


if __name__ == "__main__":
    main()