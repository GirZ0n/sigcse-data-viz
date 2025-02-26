from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from welcome.data_input import ZipData


@st.cache_data(show_spinner="Loading window data")
def load_tool_window_data(zip_data: ZipData) -> pd.DataFrame:
    tool_window_data = zip_data.toolwindowdata[["research_id", "date", "action", "active_window"]]

    tool_window_data["date"] = pd.to_datetime(tool_window_data["date"], format="mixed")
    tool_window_data.dropna(subset=["active_window"], inplace=True)

    researches = zip_data.researches[["id", "user"]]
    researches = researches.rename(columns={"id": "research_id"})
    researches = researches.convert_dtypes()

    data = pd.merge(tool_window_data, researches, on="research_id")
    data = data[data["user"] != 20]

    return data


def show_top_windows_page():
    if st.session_state.get("zip_data") is None:
        st.error(f"You can't access this page without passing data.")
        st.stop()

    zip_data = st.session_state["zip_data"]

    # ----------------------------------------------------------------

    st.title("Top Windows")

    tool_window_data = load_tool_window_data(zip_data)

    with st.expander("Config", expanded=True):
        left, right = st.columns(2, vertical_alignment="center")

        with left:
            top = st.number_input("Top", value=2, min_value=1, max_value=tool_window_data["active_window"].nunique())

        left, right = st.columns(2, vertical_alignment="center")

        with left:
            ascending = st.toggle("Ascending", key="top_windows_ascending")

        with right:
            normalize = st.toggle("Normalize", value=True)

        top_stats = (
            tool_window_data.groupby("user")
            .apply(lambda group: group["active_window"].unique())
            .explode()
            .value_counts(ascending=ascending)
        )

        if normalize:
            top_stats /= tool_window_data["user"].nunique()
            top_stats *= 100

        top_stats = top_stats.reset_index()

        st.divider()

        filter_mode = st.radio("Filter Mode", ["Exclude", "Include"], horizontal=True, key="top_windows_filter_mode")

        select = st.multiselect("Filter", top_stats["index"].unique())

        if select:
            mask = top_stats["index"].isin(select)

            if filter_mode == "Exclude":
                top_stats = top_stats[~mask]
            else:
                top_stats = top_stats[mask]

        top_stats = top_stats.head(top)

    fig = px.bar(top_stats, x="index", y="count")

    fig.update_xaxes(title="Window")
    fig.update_yaxes(title="Number of Users " + (" (%)" if normalize else ""))

    st.plotly_chart(fig)
