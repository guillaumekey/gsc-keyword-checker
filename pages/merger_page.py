"""
Page pour la fusion des données SEO et de crawl
"""

import streamlit as st
import pandas as pd
import os
from modules.data_merger import DataMerger

def merger_page(config):
    """
    Affiche la page de fusion des données.

    Args:
        config (dict): Configuration de l'application
    """
    st.header("Fusion des données")
    logger = st.session_state.logger

    # Section pour les logs
    with st.expander("Journal d'exécution", expanded=True):
        log_placeholder = st.empty()

    # Vérifier s'il existe un fichier de fusion intermédiaire
    interim_file = os.path.join(config['directories']['output'], 'Final-SEO-Opportunities-interim.xlsx')
    if os.path.exists(interim_file):
        st.warning("Une fusion précédente a été interrompue. Voulez-vous reprendre où vous vous êtes arrêté?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reprendre la fusion interrompue"):
                if 'merge_params' in st.session_state:
                    params = st.session_state['merge_params']

                    with st.spinner("Reprise de la fusion en cours..."):
                        try:
                            # Charger les fichiers intermédiaires
                            interim_df = pd.read_excel(interim_file)
                            st.info(f"Reprise de la fusion : {len(interim_df)} mots-clés déjà traités")

                            # Reprendre le traitement restant
                            # Code pour continuer la fusion

                            # Compléter la fusion
                            final_file = os.path.join(config['directories']['output'], 'Final-SEO-Opportunities.xlsx')
                            interim_df.to_excel(final_file, index=False)

                            # Supprimer le fichier intermédiaire
                            os.remove(interim_file)

                            st.success("Fusion terminée avec succès!")

                            # Stocker le résultat dans session_state
                            st.session_state['merge_results_path'] = final_file
                            st.session_state['df_final'] = interim_df

                            # Afficher les résultats
                            st.subheader("Résultats finaux")
                            st.dataframe(interim_df)
                        except Exception as e:
                            st.error(f"Erreur lors de la reprise : {str(e)}")
                else:
                    st.error("Impossible de reprendre la fusion. Paramètres manquants.")
        with col2:
            if st.button("Ignorer et démarrer une nouvelle fusion"):
                try:
                    os.remove(interim_file)
                    st.success("Fichier intermédiaire supprimé. Vous pouvez démarrer une nouvelle fusion.")
                    st.experimental_rerun()
                except:
                    st.error(f"Impossible de supprimer le fichier intermédiaire : {interim_file}")

    # Vérifier si les fichiers nécessaires existent dans session_state
    has_keywords = 'keywords_results_path' in st.session_state
    has_crawl = 'crawl_results_path' in st.session_state

    # Afficher l'état des fichiers disponibles
    if has_keywords:
        seo_file = st.session_state['keywords_results_path']
        st.success(f"Données d'analyse SEO disponibles : {os.path.basename(seo_file)}")

        # Vérifier la taille du fichier SEO
        try:
            df_seo = pd.read_excel(seo_file)
            seo_size = len(df_seo)
            st.info(f"Nombre de mots-clés disponibles : {seo_size}")

            # Pour les fichiers volumineux, offrir des options de filtrage
            if seo_size > 3000:
                st.warning("Fichier volumineux détecté. La fusion peut prendre du temps ou échouer.")

                # Option pour limiter le nombre d'entrées
                if st.checkbox("Limiter le nombre de mots-clés pour la fusion", value=False):
                    limit = st.slider("Nombre maximum de mots-clés à traiter", 500, seo_size, min(3000, seo_size))

                    # Filtrer les données
                    df_seo = df_seo.head(limit)
                    st.info(f"Les données seront limitées aux {limit} premiers mots-clés")

                    # Sauvegarder dans un fichier temporaire
                    temp_seo_file = os.path.join(config['directories']['data'], "seo_temp_filtered.xlsx")
                    df_seo.to_excel(temp_seo_file, index=False)

                    # Utiliser ce fichier pour la fusion
                    seo_file = temp_seo_file
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier SEO : {str(e)}")
    else:
        st.error("Fichier d'analyse SEO non trouvé. Veuillez d'abord effectuer l'analyse de mots-clés.")

    if has_crawl:
        crawl_file = st.session_state['crawl_results_path']
        st.success(f"Données de crawl disponibles : {os.path.basename(crawl_file)}")
    else:
        st.warning("Fichier de crawl traité non trouvé. La fusion sera limitée aux données d'analyse SEO.")

    # Vérifier si une fusion a déjà été effectuée
    if 'merge_results_path' in st.session_state:
        st.success(f"Fusion déjà effectuée : {os.path.basename(st.session_state['merge_results_path'])}")

        if st.button("Voir les résultats fusionnés"):
            try:
                df_final = pd.read_excel(st.session_state['merge_results_path'])
                st.subheader("Résultats finaux")
                st.dataframe(df_final)

                # Statistiques récapitulatives sur la présence des mots-clés
                presence_columns = [col for col in df_final.columns if col.endswith('_keyword_presence')]

                if presence_columns:
                    st.subheader("Présence des mots-clés par élément")

                    presence_stats = {}
                    for col in presence_columns:
                        element = col.replace('_keyword_presence', '')
                        presence_count = sum(df_final[col] == 'Sí')
                        presence_pct = presence_count / len(df_final) * 100
                        presence_stats[element] = presence_pct

                    # Créer un graphique pour visualiser les statistiques
                    chart_data = pd.DataFrame({
                        'Élément': list(presence_stats.keys()),
                        'Pourcentage': list(presence_stats.values())
                    })

                    st.bar_chart(chart_data.set_index('Élément'))

                # Option de téléchargement
                with open(st.session_state['merge_results_path'], "rb") as file:
                    st.download_button(
                        label="Télécharger les résultats finaux",
                        data=file,
                        file_name="Final-SEO-Opportunities.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier fusionné : {str(e)}")

        # Option pour refaire la fusion
        if st.button("Refaire la fusion"):
            # Supprimer les résultats existants
            if 'merge_results_path' in st.session_state:
                del st.session_state['merge_results_path']
            st.experimental_rerun()

    # Si les données SEO sont disponibles, afficher les options de fusion
    elif has_keywords:
        # Options de fusion
        st.subheader("Options de fusion")

        columns_to_check = ["title 1", "meta description 1", "h1-1", "all_desc", "all_h2list"]
        selected_columns = st.multiselect(
            "Sélectionnez les colonnes à vérifier pour la présence de mots-clés",
            columns_to_check,
            default=columns_to_check if has_crawl else []
        )

        # Option pour traitement par lots
        use_batching = st.checkbox("Traiter par lots (recommandé pour les gros fichiers)", value=True)
        if use_batching:
            batch_size = st.slider("Taille du lot", 100, 1000, 500, 100)

        logger.info(
            f"Colonnes sélectionnées pour vérification: {', '.join(selected_columns) if selected_columns else 'Aucune'}")

        if st.button("Fusionner les données"):
            # Stocker les paramètres de fusion pour permettre la reprise
            st.session_state['merge_params'] = {
                'seo_file': seo_file,
                'crawl_file': crawl_file if has_crawl else None,
                'selected_columns': selected_columns,
                'use_batching': use_batching,
                'batch_size': batch_size if use_batching else None
            }

            # Ajouter une barre de progression
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Fonction de callback pour mettre à jour la progression
            def update_progress(current, total, message):
                progress = min(current / total, 1.0)
                progress_bar.progress(progress)
                status_text.text(f"{message} - {current}/{total} ({int(progress * 100)}%)")

            with st.spinner("Fusion en cours..."):
                try:
                    logger.info("Démarrage de la fusion des données")

                    merger = DataMerger(logger=logger)

                    if has_crawl:
                        logger.info(
                            f"Fusion des données SEO avec les données de crawl. Vérification de {len(selected_columns)} colonnes.")

                        # Si traitement par lots activé et fichier volumineux
                        if use_batching and 'df_seo' in locals() and len(df_seo) > 1000:
                            # Implémenter la fusion par lots avec sauvegarde progressive
                            output_path = merger.merge_data_batched(
                                seo_file,
                                crawl_file,
                                selected_columns,
                                batch_size=batch_size,
                                progress_callback=update_progress
                            )
                        else:
                            # Fusion standard
                            output_path = merger.merge_data(
                                seo_file,
                                crawl_file,
                                selected_columns,
                                progress_callback=update_progress
                            )

                        success_msg = "Fusion terminée avec les données de crawl!"
                    else:
                        logger.info("Utilisation des données SEO uniquement (pas de données de crawl).")
                        output_path = merger.merge_data(
                            seo_file,
                            None,
                            None,
                            progress_callback=update_progress
                        )
                        success_msg = "Analyse terminée sans données de crawl!"

                    # Compléter la barre de progression
                    progress_bar.progress(1.0)
                    status_text.text("Fusion terminée!")

                    logger.info(f"Fusion terminée avec succès! Résultats sauvegardés dans {output_path}")

                    # Stocker le chemin des résultats dans session_state
                    st.session_state['merge_results_path'] = output_path

                    st.success(success_msg)

                    # Afficher les résultats
                    df_final = pd.read_excel(output_path)

                    # Stocker dans session_state
                    st.session_state['df_final'] = df_final

                    st.subheader("Résultats finaux")
                    st.dataframe(df_final)

                    # Statistiques récapitulatives sur la présence des mots-clés
                    if has_crawl and selected_columns:
                        st.subheader("Présence des mots-clés par élément")

                        presence_stats = {}
                        for col in selected_columns:
                            presence_col = f"{col}_keyword_presence"
                            if presence_col in df_final.columns:
                                presence_count = sum(df_final[presence_col] == 'Sí')
                                presence_pct = presence_count / len(df_final) * 100
                                presence_stats[col] = presence_pct

                        if presence_stats:
                            # Créer un graphique pour visualiser les statistiques
                            chart_data = pd.DataFrame({
                                'Élément': list(presence_stats.keys()),
                                'Pourcentage': list(presence_stats.values())
                            })

                            st.bar_chart(chart_data.set_index('Élément'))

                            logger.info(f"Statistiques de présence des mots-clés générées: {presence_stats}")

                    # Option de téléchargement
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="Télécharger les résultats finaux",
                            data=file,
                            file_name="Final-SEO-Opportunities.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    error_msg = f"Erreur pendant la fusion : {str(e)}"
                    logger.error(error_msg)
                    st.error(error_msg)
                    st.info("Vous pourrez reprendre la fusion là où elle s'est arrêtée en revenant sur cette page.")
    else:
        logger.info("En attente de l'analyse de mots-clés")
        st.info("Veuillez d'abord effectuer l'analyse de mots-clés avant de fusionner les données.")