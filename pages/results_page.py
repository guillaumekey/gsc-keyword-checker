"""
Page d'affichage des résultats et statistiques
"""

import streamlit as st
import pandas as pd
import os
import datetime


def results_page(config):
    """
    Affiche la page des résultats et statistiques.

    Args:
        config (dict): Configuration de l'application
    """
    st.header("Résultats")
    logger = st.session_state.logger

    # Récupérer tous les chemins de résultats stockés dans session_state
    available_results = []

    if 'keywords_results_path' in st.session_state:
        available_results.append(('Analyse SEO', st.session_state['keywords_results_path']))

    if 'crawl_results_path' in st.session_state:
        available_results.append(('Données de crawl', st.session_state['crawl_results_path']))

    if 'merge_results_path' in st.session_state:
        available_results.append(('Fusion des données', st.session_state['merge_results_path']))

    if available_results:
        st.success(f"{len(available_results)} fichiers de résultats disponibles en mémoire")

        # Afficher les options
        result_options = [f"{name}: {os.path.basename(path)}" for name, path in available_results]
        selected_option = st.selectbox("Sélectionnez un fichier à visualiser", result_options)

        # Trouver le fichier sélectionné
        selected_index = result_options.index(selected_option)
        selected_name, selected_path = available_results[selected_index]

        if st.button("Charger le fichier"):
            try:
                logger.info(f"Chargement du fichier {selected_path}")
                df = pd.read_excel(selected_path)

                # Statistiques générales sur le fichier
                rows = len(df)
                cols = len(df.columns)

                logger.info(f"Fichier chargé: {rows} lignes, {cols} colonnes")

                st.write(f"Aperçu de {os.path.basename(selected_path)}:")
                st.dataframe(df)

                # Statistiques
                st.subheader("Statistiques")

                # Informations de base sur le fichier
                file_size = os.path.getsize(selected_path) / (1024 * 1024)  # Taille en Mo
                modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(selected_path))

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Nombre de lignes", rows)
                with col2:
                    st.metric("Nombre de colonnes", cols)
                with col3:
                    st.metric("Taille du fichier", f"{file_size:.2f} Mo")

                st.caption(f"Dernière modification: {modification_time}")

                # Statistiques spécifiques selon le type de fichier
                if "is_positioned" in df.columns:
                    # C'est un fichier d'analyse SEO
                    logger.info("Génération de statistiques pour un fichier d'analyse SEO")

                    position_stats = df["is_positioned"].value_counts()

                    # Visualisation avec graphique
                    st.subheader("Répartition du positionnement")

                    # Créer un DataFrame pour le graphique
                    chart_data = pd.DataFrame({
                        'Statut': position_stats.index,
                        'Nombre': position_stats.values
                    })

                    st.bar_chart(chart_data.set_index('Statut'))

                    # Métriques
                    yes_count = len(df[df["is_positioned"] == "Yes"]) if "Yes" in df["is_positioned"].values else 0
                    wrong_page_count = len(df[df["is_positioned"] == "Yes with wrong page"]) if "Yes with wrong page" in \
                                                                                                df[
                                                                                                    "is_positioned"].values else 0
                    no_count = len(df[df["is_positioned"] == "No"]) if "No" in df["is_positioned"].values else 0

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Mots-clés bien positionnés", yes_count,
                                  f"{yes_count / len(df) * 100:.1f}%" if len(df) > 0 else "0%")
                    with col2:
                        st.metric("Mots-clés mal positionnés", wrong_page_count,
                                  f"{wrong_page_count / len(df) * 100:.1f}%" if len(df) > 0 else "0%")
                    with col3:
                        st.metric("Mots-clés non positionnés", no_count,
                                  f"{no_count / len(df) * 100:.1f}%" if len(df) > 0 else "0%")

                    # Statistiques sur les colonnes numériques
                    if "position" in df.columns and df["position"].notna().any():
                        st.subheader("Statistiques de positionnement")

                        # Calculer les statistiques pour les positions valides
                        position_stats = df[df["position"].notna()]["position"].describe()

                        # Afficher les statistiques
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Position moyenne", f"{position_stats['mean']:.2f}")
                        with col2:
                            st.metric("Position médiane", f"{position_stats['50%']:.2f}")
                        with col3:
                            st.metric("Meilleure position", f"{position_stats['min']:.2f}")
                        with col4:
                            st.metric("Pire position", f"{position_stats['max']:.2f}")

                # Vérifier si c'est un fichier de fusion avec des colonnes de présence de mot-clé
                presence_columns = [col for col in df.columns if col.endswith('_keyword_presence')]

                if presence_columns:
                    logger.info(
                        f"Génération de statistiques pour {len(presence_columns)} colonnes de présence de mot-clé")

                    st.subheader("Présence des mots-clés dans les éléments")

                    # Créer un DataFrame pour le graphique
                    presence_data = {}
                    for col in presence_columns:
                        # Extraire le nom de l'élément (retirer le suffixe '_keyword_presence')
                        element = col.replace('_keyword_presence', '')

                        # Calculer le pourcentage de présence
                        presence_count = sum(df[col] == 'Sí')
                        presence_pct = presence_count / len(df) * 100 if len(df) > 0 else 0

                        presence_data[element] = presence_pct

                    # Créer un DataFrame pour le graphique
                    chart_data = pd.DataFrame({
                        'Élément': list(presence_data.keys()),
                        'Pourcentage': list(presence_data.values())
                    })

                    st.bar_chart(chart_data.set_index('Élément'))

                # Option de téléchargement
                with open(selected_path, "rb") as file:
                    st.download_button(
                        label="Télécharger ce fichier",
                        data=file,
                        file_name=os.path.basename(selected_path),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                logger.info("Affichage des statistiques terminé")

            except Exception as e:
                error_msg = f"Erreur lors de la lecture du fichier: {str(e)}"
                logger.error(error_msg)
                st.error(error_msg)
    else:
        # Si aucun résultat n'est en mémoire, chercher les fichiers sur le disque
        logger.info("Aucun fichier de résultats en mémoire. Recherche sur le disque...")
        output_dir = config['directories']['output']
        os.makedirs(output_dir, exist_ok=True)
        results_files = [f for f in os.listdir(output_dir) if f.endswith('.xlsx')]

        logger.info(f"Recherche des fichiers de résultats dans {output_dir}")
        logger.info(f"{len(results_files)} fichiers trouvés: {', '.join(results_files)}")

        if not results_files:
            logger.info("Aucun fichier de résultats trouvé")
            st.info("Aucun fichier de résultats trouvé. Veuillez effectuer une analyse.")
        else:
            st.subheader("Fichiers de résultats disponibles sur le disque")

            selected_file = st.selectbox("Sélectionnez un fichier à visualiser", results_files)
            file_path = os.path.join(output_dir, selected_file)

            logger.info(f"Fichier sélectionné: {selected_file}")

            if st.button("Charger le fichier"):
                try:
                    logger.info(f"Chargement du fichier {file_path}")
                    df = pd.read_excel(file_path)

                    # Stocker le chemin dans session_state pour la prochaine fois
                    if 'SEO-Opportunities' in selected_file:
                        st.session_state['keywords_results_path'] = file_path
                    elif 'crawl-client-updated' in selected_file:
                        st.session_state['crawl_results_path'] = file_path
                    elif 'Final-SEO-Opportunities' in selected_file:
                        st.session_state['merge_results_path'] = file_path

                    # Continuer avec l'affichage comme avant
                    # ...

                    # Afficher l'aperçu des données
                    st.write(f"Aperçu de {selected_file}:")
                    st.dataframe(df)

                    # Statistiques de base
                    st.subheader("Statistiques")

                    # Informations sur le fichier
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Taille en Mo
                    modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Nombre de lignes", len(df))
                    with col2:
                        st.metric("Nombre de colonnes", len(df.columns))
                    with col3:
                        st.metric("Taille du fichier", f"{file_size:.2f} Mo")

                    st.caption(f"Dernière modification: {modification_time}")

                    # Reste du code pour les statistiques spécifiques...
                    # (similaire à la partie précédente)

                except Exception as e:
                    error_msg = f"Erreur lors de la lecture du fichier: {str(e)}"
                    logger.error(error_msg)
                    st.error(error_msg)