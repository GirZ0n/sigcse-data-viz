import streamlit as st

from welcome.data_input import show_data_input_page
from welcome.readme import show_readme_page

README_PAGE = st.Page(show_readme_page, title="README", icon=':material/bookmark:', default=True)
DATA_INPUT_PAGE = st.Page(show_data_input_page, title="Data Input", icon=':material/database:')

WELCOME_PAGES = [README_PAGE, DATA_INPUT_PAGE]
