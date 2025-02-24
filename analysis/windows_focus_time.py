from pathlib import Path
from typing import Literal

import pandas as pd
import streamlit as st

from analysis.top_windows import load_tool_window_data

import plotly.express as px

from welcome.data_input import ZipData


@st.cache_data(show_spinner="Loading duration data")
def load_duration_data(zip_data: ZipData) -> pd.DataFrame:
    tool_window_data = load_tool_window_data(zip_data)

    tool_window_data = tool_window_data[tool_window_data["action"] == "FOCUSED"]
    tool_window_data.drop(columns=["action"], inplace=True)

    tool_window_data = (
        tool_window_data.groupby("research_id")
        .apply(
            lambda group: group.loc[group["active_window"].shift() != group["active_window"]],
        )
        .reset_index(drop=True)
    )

    tool_window_data["duration"] = (
        tool_window_data.groupby("research_id")
        .apply(lambda group: (group["date"].shift(-1) - group["date"]).dt.total_seconds())
        .reset_index(drop=True)
    )

    tool_window_data.dropna(subset=["duration"], inplace=True)
    tool_window_data.drop(columns=["date", "research_id"], inplace=True)

    duration_data = tool_window_data.groupby(["user", "active_window"]).sum().reset_index()
    duration_data.drop(columns=["user"], inplace=True)

    return duration_data


def _normalize_duration(duration: float, scale: Literal["Seconds", "Minutes", "Hours"]) -> float:
    if scale == "Seconds":
        return duration

    if scale == "Minutes":
        return duration / 60

    if scale == "Hours":
        return duration / 3600

    raise ValueError(f"Invalid value for `scale`: {scale}")


def show_window_focus_time_page():
    if st.session_state.get("zip_data") is None:
        st.error(f"You can't access this page without passing data.")
        st.stop()

    zip_data = st.session_state["zip_data"]

    st.title("Window Focus Time")

    duration_data = load_duration_data(zip_data)

    with st.expander("Config", expanded=True):
        left, right = st.columns(2, vertical_alignment="center")

        with left:
            top = st.number_input("Top", value=10, min_value=1, max_value=len(duration_data["active_window"].unique()))

        with right:
            scale = st.radio("Scale", ["Seconds", "Minutes", "Hours"], horizontal=True)

        ascending = st.toggle("Ascending", key="window_focus_time_ascending")

        stats = (
            duration_data.groupby("active_window", as_index=False)["duration"]
            .sum()
            .sort_values("duration", ascending=ascending)
        )

        duration_data["duration"] = duration_data["duration"].apply(lambda x: _normalize_duration(x, scale))

        st.divider()

        filter_mode = st.radio(
            "Filter Mode",
            ["Exclude", "Include"],
            horizontal=True,
            key="window_focus_time_filter_mode",
        )

        select = st.multiselect("Filter", stats["active_window"].unique())

        if select:
            duration_mask = duration_data["active_window"].isin(select)
            stats_mask = stats["active_window"].isin(select)

            if filter_mode == "Exclude":
                duration_data = duration_data[~duration_mask]
                stats = stats[~stats_mask]
            else:
                duration_data = duration_data[duration_mask]
                stats = stats[stats_mask]

        duration_data = duration_data[duration_data["active_window"].isin(stats.head(top)["active_window"])]

    fig = px.box(duration_data, x="active_window", y="duration")

    fig.update_xaxes(title="Window")
    fig.update_yaxes(title="Total Time " + f"({scale.lower()})")
    fig.update_xaxes(categoryorder="sum " + ("ascending" if ascending else "descending"))

    st.plotly_chart(fig)
