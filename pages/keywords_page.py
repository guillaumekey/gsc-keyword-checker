"""
Page d'analyse des mots-clés avec Google Search Console
"""

import streamlit as st
import pandas as pd
import os
import datetime
from modules.gsc_manager import GSCManager
from modules.keyword_analyzer import KeywordAnalyzer


def keywords_page(config, site_url, start_date, end_date):
    """
    Affiche la page d'analyse de mots-clés.

    Args:
        config (dict): Configuration de l'application
        site_url (str): URL du site à analyser
        start_date (datetime.date): Date de début de l'analyse
        end_date (datetime.date): Date de fin de l'analyse
    """
    st.header("Analyse de mots-clés")
    logger = st.session_state.logger

    # Section pour les logs
    with st.expander("Journal d'exécution", expanded=True):
        log_placeholder = st.empty()

    # Vérifier s'il existe un fichier de sauvegarde intermédiaire
    interim_file = os.path.join(config['directories']['output'], 'SEO-Opportunities-interim.xlsx')
    if os.path.exists(interim_file):
        st.warning("Une analyse précédente a été interrompue. Voulez-vous reprendre où vous vous êtes arrêté?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reprendre l'analyse interrompue"):
                if 'df_keywords' in st.session_state and 'analysis_params' in st.session_state:
                    params = st.session_state['analysis_params']

                    with st.spinner("Reprise de l'analyse en cours..."):
                        # Afficher les paramètres de l'analyse précédente
                        st.info(
                            f"Reprise de l'analyse avec les paramètres : Site={params['site_url']}, Période={params['start_date']} au {params['end_date']}")

                        # Ajouter une barre de progression
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        # Fonction de callback pour mettre à jour la progression
                        def update_progress(current, total, message):
                            progress = min(current / total, 1.0)
                            progress_bar.progress(progress)
                            status_text.text(f"{message} - {current}/{total} ({int(progress * 100)}%)")

                        # Créer le gestionnaire GSC
                        gsc_manager = GSCManager(
                            client_secret_file=config['gsc']['client_secret_file'],
                            token_file=config['gsc']['token_file'],
                            logger=logger
                        )

                        # Analyser les mots-clés
                        analyzer = KeywordAnalyzer(gsc_manager, logger=logger)

                        # Créer un fichier temporaire si nécessaire
                        temp_path = os.path.join(config['directories']['data'], "keywords_temp.csv")
                        if not os.path.exists(temp_path):
                            st.session_state['df_keywords'].to_csv(temp_path, index=False)

                        results_path = analyzer.analyze_keywords(
                            temp_path,
                            params['site_url'],
                            params['start_date'],
                            params['end_date'],
                            params['batch_size'],
                            progress_callback=update_progress
                        )

                        # Compléter la barre de progression
                        progress_bar.progress(1.0)
                        status_text.text("Analyse terminée!")

                        logger.info(f"Reprise terminée avec succès! Résultats sauvegardés dans {results_path}")

                        # Stocker le chemin des résultats dans session_state
                        st.session_state['keywords_results_path'] = results_path

                        # Afficher les résultats
                        df_results = pd.read_excel(results_path)

                        # Stocker les résultats dans session_state
                        st.session_state['df_keywords_results'] = df_results

                        st.success(f"Analyse terminée ! Résultats sauvegardés.")

                        # Afficher les résultats et statistiques comme dans le code original
                        show_keywords_results(df_results, logger)
                else:
                    st.error("Impossible de reprendre l'analyse. Paramètres manquants.")
        with col2:
            if st.button("Ignorer et démarrer une nouvelle analyse"):
                try:
                    os.remove(interim_file)
                    st.success("Fichier intermédiaire supprimé. Vous pouvez démarrer une nouvelle analyse.")
                    st.experimental_rerun()
                except:
                    st.error(f"Impossible de supprimer le fichier intermédiaire : {interim_file}")

    # Vérifier si un fichier a déjà été chargé dans une session précédente
    if 'df_keywords' in st.session_state and 'keywords_filename' in st.session_state:
        st.success(f"Fichier déjà chargé : {st.session_state['keywords_filename']}")

        # Afficher des informations sur le fichier
        df_keywords = st.session_state['df_keywords']
        keywords_count = len(df_keywords)

        # Pour les fichiers volumineux, offrir des options de traitement par tranches
        if keywords_count > 1000:
            st.info(f"Fichier volumineux détecté : {keywords_count} mots-clés")

            # Options pour le traitement de gros fichiers
            with st.expander("Options pour fichiers volumineux", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    process_all = st.checkbox("Traiter tous les mots-clés", value=True)

                if not process_all:
                    with col2:
                        tranche_size = st.slider("Taille de la tranche", 500, min(5000, keywords_count), 1000)

                    # Sélectionner le début de la tranche
                    max_start = max(0, keywords_count - tranche_size)
                    start_index = st.slider("Commencer à l'index", 0, max_start, 0)
                    end_index = min(start_index + tranche_size, keywords_count)

                    st.info(f"Traitement des mots-clés {start_index} à {end_index} (sur {keywords_count})")

                    # Filtrer les mots-clés
                    df_keywords_filtered = df_keywords.iloc[start_index:end_index].copy()
                    st.dataframe(df_keywords_filtered.head())

                    # Stocker la tranche filtrée
                    st.session_state['df_keywords_filtered'] = df_keywords_filtered
                    temp_path = os.path.join(config['directories']['data'], "keywords_temp_filtered.csv")
                    df_keywords_filtered.to_csv(temp_path, index=False)
                else:
                    # Utiliser tous les mots-clés
                    st.session_state['df_keywords_filtered'] = df_keywords
        else:
            # Pour les petits fichiers, utiliser tous les mots-clés
            st.session_state['df_keywords_filtered'] = df_keywords

        with st.expander("Voir les données chargées", expanded=True):
            st.dataframe(st.session_state['df_keywords_filtered'].head(10))
            st.caption(f"Affichage de 10 lignes sur {len(st.session_state['df_keywords_filtered'])} mots-clés")

        # Offrir la possibilité de charger un autre fichier
        if st.button("Charger un nouveau fichier"):
            # Supprimer les données existantes
            if 'df_keywords' in st.session_state:
                del st.session_state['df_keywords']
            if 'keywords_filename' in st.session_state:
                del st.session_state['keywords_filename']
            if 'df_keywords_filtered' in st.session_state:
                del st.session_state['df_keywords_filtered']
            st.experimental_rerun()

        # Continuer avec les options d'analyse comme avant
        st.subheader("Options d'analyse")
        batch_size = st.slider("Taille du lot de mots-clés", min_value=1, max_value=50, value=10,
                               help="Nombre de mots-clés traités en une seule fois. Une valeur plus petite peut aider à éviter les erreurs avec les gros fichiers.")

        # Authentification GSC
        st.subheader("Authentification Google Search Console")
        st.info(
            "L'authentification à Google Search Console est nécessaire pour récupérer les données de positionnement.")

        if st.button("Lancer l'analyse"):
            try:
                logger.info(
                    f"Démarrage de l'analyse avec {len(st.session_state['df_keywords_filtered'])} mots-clés. Taille de lot: {batch_size}")
                logger.info(f"Période d'analyse: {start_date} au {end_date}")

                # Stocker les paramètres d'analyse dans session_state pour permettre la reprise
                st.session_state['analysis_params'] = {
                    'site_url': site_url,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'batch_size': batch_size
                }

                # Ajouter une barre de progression
                progress_bar = st.progress(0)
                status_text = st.empty()

                with st.spinner("Analyse en cours..."):
                    # Créer le gestionnaire GSC
                    logger.info("Initialisation de la connexion à Google Search Console...")
                    gsc_manager = GSCManager(
                        client_secret_file=config['gsc']['client_secret_file'],
                        token_file=config['gsc']['token_file'],
                        logger=logger
                    )

                    # Analyser les mots-clés
                    analyzer = KeywordAnalyzer(gsc_manager, logger=logger)

                    # Fonction de callback pour mettre à jour la progression
                    def update_progress(current, total, message):
                        progress = min(current / total, 1.0)
                        progress_bar.progress(progress)
                        status_text.text(f"{message} - {current}/{total} ({int(progress * 100)}%)")

                    # Créer un fichier temporaire avec les mots-clés filtrés
                    temp_path = os.path.join(config['directories']['data'], "keywords_temp_filtered.csv")
                    st.session_state['df_keywords_filtered'].to_csv(temp_path, index=False)

                    results_path = analyzer.analyze_keywords(
                        temp_path,
                        site_url,
                        start_date.strftime('%Y-%m-%d'),
                        end_date.strftime('%Y-%m-%d'),
                        batch_size,
                        progress_callback=update_progress
                    )

                    # Compléter la barre de progression
                    progress_bar.progress(1.0)
                    status_text.text("Analyse terminée!")

                    logger.info(f"Analyse terminée avec succès! Résultats sauvegardés dans {results_path}")

                    # Stocker le chemin des résultats dans session_state
                    st.session_state['keywords_results_path'] = results_path

                    # Afficher les résultats
                    df_results = pd.read_excel(results_path)

                    # Stocker les résultats dans session_state
                    st.session_state['df_keywords_results'] = df_results

                    st.success(f"Analyse terminée ! Résultats sauvegardés.")

                    # Afficher les résultats et statistiques
                    show_keywords_results(df_results, logger)
            except Exception as e:
                error_msg = f"Erreur pendant l'analyse : {str(e)}"
                logger.error(error_msg)
                st.error(error_msg)
                st.info("Vous pourrez reprendre l'analyse là où elle s'est arrêtée en revenant sur cette page.")
    else:
        # Upload du fichier CSV
        uploaded_file = st.file_uploader("Téléchargez votre fichier CSV avec URLs et mots-clés", type=["csv"])

        if uploaded_file is not None:
            # Prévisualisation des données
            try:
                logger.info(f"Lecture du fichier CSV: {uploaded_file.name}")
                df_keywords = pd.read_csv(uploaded_file)

                # Stocker dans session_state
                st.session_state['df_keywords'] = df_keywords
                st.session_state['keywords_filename'] = uploaded_file.name

                st.write("Aperçu des données:")
                st.dataframe(df_keywords.head())
                logger.info(f"Fichier chargé avec succès. {len(df_keywords)} mots-clés trouvés.")

                # Vérification des colonnes requises
                required_columns = ["url", "palabra clave"]
                missing_columns = [col for col in required_columns if col not in df_keywords.columns]

                if missing_columns:
                    error_msg = f"Colonnes manquantes dans le fichier CSV: {', '.join(missing_columns)}"
                    logger.error(error_msg)
                    st.error(error_msg)
                    st.markdown("Le fichier doit contenir les colonnes `url` et `palabra clave`.")

                    # Supprimer les données incorrectes
                    if 'df_keywords' in st.session_state:
                        del st.session_state['df_keywords']
                    if 'keywords_filename' in st.session_state:
                        del st.session_state['keywords_filename']
                else:
                    logger.info("Structure du fichier valide. Toutes les colonnes requises sont présentes.")

                    # Sauvegarde temporaire du fichier
                    temp_path = os.path.join(config['directories']['data'], "keywords_temp.csv")
                    df_keywords.to_csv(temp_path, index=False)
                    logger.info(f"Fichier temporaire sauvegardé: {temp_path}")

                    # Rafraîchir la page pour afficher les options d'analyse
                    st.experimental_rerun()
            except Exception as e:
                error_msg = f"Erreur lors de la lecture du fichier: {str(e)}"
                logger.error(error_msg)
                st.error(error_msg)
        else:
            st.info("Veuillez télécharger un fichier CSV contenant deux colonnes: 'url' et 'palabra clave'.")

            # Template d'exemple
            st.subheader("Format attendu")
            example_df = pd.DataFrame({
                "url": ["https://www.example.com/page1", "https://www.example.com/page2"],
                "palabra clave": ["mot clé 1", "mot clé 2"]
            })
            st.dataframe(example_df)

            # Bouton pour télécharger un template
            csv = example_df.to_csv(index=False)
            st.download_button(
                label="Télécharger un template CSV",
                data=csv,
                file_name="template_keywords.csv",
                mime="text/csv",
            )


def show_keywords_results(df_results, logger):
    """
    Affiche les résultats et statistiques d'analyse des mots-clés.

    Args:
        df_results (DataFrame): DataFrame contenant les résultats de l'analyse
        logger (Logger): Logger pour journaliser les opérations
    """
    st.subheader("Résultats de l'analyse")
    st.dataframe(df_results)

    # Statistiques récapitulatives
    positioned_count = len(df_results[df_results['is_positioned'] == 'Yes'])
    wrong_page_count = len(df_results[df_results['is_positioned'] == 'Yes with wrong page'])
    not_positioned_count = len(df_results[df_results['is_positioned'] == 'No'])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Mots-clés bien positionnés", positioned_count, f"{positioned_count / len(df_results) * 100:.1f}%")
    with col2:
        st.metric("Mots-clés mal positionnés", wrong_page_count, f"{wrong_page_count / len(df_results) * 100:.1f}%")
    with col3:
        st.metric("Mots-clés non positionnés", not_positioned_count,
                  f"{not_positioned_count / len(df_results) * 100:.1f}%")

    logger.info(
        f"Statistiques: {positioned_count} bien positionnés, {wrong_page_count} mal positionnés, {not_positioned_count} non positionnés")

    # Graphique de répartition
    st.subheader("Répartition du positionnement")
    position_data = {
        'Statut': ['Bien positionnés', 'Mal positionnés', 'Non positionnés'],
        'Nombre': [positioned_count, wrong_page_count, not_positioned_count]
    }
    position_df = pd.DataFrame(position_data)
    st.bar_chart(position_df.set_index('Statut'))

    # Option de téléchargement
    with open(st.session_state['keywords_results_path'], "rb") as file:
        st.download_button(
            label="Télécharger les résultats",
            data=file,
            file_name="SEO-Opportunities.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )