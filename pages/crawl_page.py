"""
Page pour le traitement des fichiers de crawl
"""

import streamlit as st
import pandas as pd
import os
from modules.crawl_processor import CrawlProcessor


def crawl_page(config):
    """
    Affiche la page de traitement des données de crawl.

    Args:
        config (dict): Configuration de l'application
    """
    st.header("Traitement des données de crawl")
    logger = st.session_state.logger

    # Section pour les logs
    with st.expander("Journal d'exécution", expanded=True):
        log_placeholder = st.empty()

    st.info("Cette étape est optionnelle. Elle permet d'ajouter des données supplémentaires à votre analyse.")

    # Vérifier si un fichier a déjà été chargé dans une session précédente
    if 'df_crawl' in st.session_state and 'crawl_filename' in st.session_state:
        st.success(f"Fichier de crawl déjà chargé : {st.session_state['crawl_filename']}")

        with st.expander("Voir les données chargées", expanded=True):
            st.dataframe(st.session_state['df_crawl'].head())

        # Offrir la possibilité de charger un autre fichier
        if st.button("Charger un nouveau fichier"):
            # Supprimer les données existantes
            if 'df_crawl' in st.session_state:
                del st.session_state['df_crawl']
            if 'crawl_filename' in st.session_state:
                del st.session_state['crawl_filename']
            if 'crawl_results_path' in st.session_state:
                del st.session_state['crawl_results_path']
            st.rerun()

        # Vérifier si les données ont déjà été traitées
        if 'crawl_results_path' in st.session_state:
            st.success(f"Données de crawl déjà traitées : {os.path.basename(st.session_state['crawl_results_path'])}")

            if st.button("Voir les données traitées"):
                try:
                    df_processed = pd.read_excel(st.session_state['crawl_results_path'])
                    st.subheader("Aperçu des données traitées")
                    st.dataframe(df_processed.head())

                    # Statistiques récapitulatives
                    cols_with_data = sum([1 for col in df_processed.columns if df_processed[col].notna().sum() > 0])

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("URLs traitées", len(df_processed))
                    with col2:
                        st.metric("Colonnes avec données", cols_with_data)
                except Exception as e:
                    st.error(f"Erreur lors de la lecture du fichier traité : {str(e)}")
        else:
            # Option pour traiter les données
            if st.button("Traiter les données de crawl"):
                # Ajouter une barre de progression
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Fonction de callback pour mettre à jour la progression
                def update_progress(current, total, message):
                    progress = min(current / total, 1.0)
                    progress_bar.progress(progress)
                    status_text.text(f"{message} - {int(progress * 100)}%")

                with st.spinner("Traitement en cours..."):
                    logger.info("Démarrage du traitement du fichier de crawl")

                    # Créer un fichier temporaire si nécessaire
                    temp_path = os.path.join(config['directories']['data'], "crawl_temp.csv")
                    st.session_state['df_crawl'].to_csv(temp_path, index=False)

                    processor = CrawlProcessor(logger=logger)
                    output_path = processor.process_crawl_data(
                        temp_path,
                        progress_callback=update_progress
                    )

                    # Compléter la barre de progression
                    progress_bar.progress(1.0)
                    status_text.text("Traitement terminé!")

                    logger.info(f"Traitement terminé avec succès! Données de crawl sauvegardées dans {output_path}")

                    # Stocker le chemin des résultats dans session_state
                    st.session_state['crawl_results_path'] = output_path

                    st.success("Traitement terminé ! Données de crawl sauvegardées.")

                    # Afficher un aperçu des résultats
                    df_processed = pd.read_excel(output_path)
                    st.subheader("Aperçu des données traitées")
                    st.dataframe(df_processed.head())

                    # Statistiques récapitulatives
                    cols_with_data = sum([1 for col in df_processed.columns if df_processed[col].notna().sum() > 0])

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("URLs traitées", len(df_processed))
                    with col2:
                        st.metric("Colonnes avec données", cols_with_data)

                    # Option de téléchargement
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="Télécharger les données traitées",
                            data=file,
                            file_name="crawl-client-updated.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
    else:
        # Upload du fichier CSV
        uploaded_file = st.file_uploader("Téléchargez votre fichier de crawl (format CSV de Screaming Frog)",
                                         type=["csv"])

        if uploaded_file is not None:
            # Prévisualisation des données
            try:
                logger.info(f"Lecture du fichier de crawl: {uploaded_file.name}")
                df_crawl = pd.read_csv(uploaded_file)

                # Stocker dans session_state
                st.session_state['df_crawl'] = df_crawl
                st.session_state['crawl_filename'] = uploaded_file.name

                # Afficher un aperçu des données
                st.write("Aperçu des données de crawl:")
                st.dataframe(df_crawl.head())

                logger.info(f"Fichier chargé avec succès. {len(df_crawl)} URLs trouvées.")

                # Vérification des colonnes souhaitées
                desired_columns = ["address", "title 1", "meta description 1", "h1-1"]

                # Convertir les noms de colonnes en minuscules pour la comparaison
                df_columns_lower = [col.lower() for col in df_crawl.columns]
                missing_columns = [col for col in desired_columns if col.lower() not in df_columns_lower]

                if missing_columns:
                    warning_msg = f"Colonnes potentiellement manquantes dans le fichier de crawl: {', '.join(missing_columns)}"
                    logger.warning(warning_msg)
                    st.warning(warning_msg)
                    st.markdown("Ces colonnes sont recommandées mais pas obligatoires.")
                else:
                    logger.info("Toutes les colonnes souhaitées sont présentes dans le fichier.")

                # Sauvegarde temporaire du fichier
                temp_path = os.path.join(config['directories']['data'], "crawl_temp.csv")
                df_crawl.to_csv(temp_path, index=False)
                logger.info(f"Fichier temporaire sauvegardé: {temp_path}")

                # Rafraîchir la page pour afficher les options de traitement
                st.rerun()
            except Exception as e:
                error_msg = f"Erreur lors de la lecture du fichier: {str(e)}"
                logger.error(error_msg)
                st.error(error_msg)
        else:
            logger.info("En attente du téléchargement d'un fichier de crawl")
            st.info("Veuillez télécharger un fichier CSV contenant les données de crawl de votre site.")