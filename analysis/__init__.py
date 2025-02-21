import streamlit as st

from analysis.top_actions import show_top_actions_page
from analysis.top_windows import show_top_windows_page
from analysis.windows_focus_time import show_window_focus_time_page

TOP_ACTIONS_PAGE = st.Page(show_top_actions_page, title="Top Actions", icon=":material/web_traffic:")
TOP_WINDOWS_PAGE = st.Page(show_top_windows_page, title="Top Windows", icon=":material/tab:")
WINDOW_FOCUS_TIME_PAGE = st.Page(show_window_focus_time_page, title="Window Focus Time", icon=":material/timer:")

ANALYSIS_PAGES = [TOP_ACTIONS_PAGE, TOP_WINDOWS_PAGE, WINDOW_FOCUS_TIME_PAGE]
