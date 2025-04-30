"""
Module pour les pages de l'application Streamlit.
Permet d'importer toutes les pages à partir d'un seul import.
"""

from pages.keywords_page import keywords_page
from pages.crawl_page import crawl_page
from pages.merger_page import merger_page
from pages.results_page import results_page

__all__ = ['keywords_page', 'crawl_page', 'merger_page', 'results_page']