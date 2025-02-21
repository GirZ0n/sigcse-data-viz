import streamlit as st

from analysis import ANALYSIS_PAGES
from welcome import WELCOME_PAGES


def main():
    pages = {'Welcome': WELCOME_PAGES, 'Analyses': ANALYSIS_PAGES}
    pg = st.navigation(pages)
    pg.run()


if __name__ == "__main__":
    main()
