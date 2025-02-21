import re
from pathlib import Path
from typing import Literal, Tuple

import pandas as pd
import streamlit as st
import plotly.express as px


def _normalize_info(value: str) -> str:
    # $<name> -> <name>
    if match := re.match(r"\$(\w+)$", value):
        return match.group(1)

    # <path>.<name_1>$<name_2> -> <name_1>.<name_2>
    # <path>.<name_1>$<name_2>$<name_3> -> <name_1>.<name_2>
    if match := re.match(r"(?:\w+\.)+(\w+)\$([a-zA-Z]+)(?:\$\w+)?$", value):
        return f"{match.group(1)}.{match.group(2)}"

    # <path>.<name_1>$<some_digit> -> <name_1>
    if match := re.match(r"(?:\w+\.)+(\w+)\$(\d+)$", value):
        return match.group(1)

    # <part_1>.<part_2>.<part_3>...<part_n> -> <part_n-1>.<part_n>
    parts = value.split(".")
    if len(parts) > 1:
        return ".".join(parts[-2:])

    return value


@st.cache_data(show_spinner='Loading data')
def load_data(data_path: Path, kind: Literal["all", "shortcut", "standalone"]) -> pd.DataFrame:
    activity_data = pd.read_csv(data_path / "activitydata.csv", usecols=["research_id", "type", "info", "action_id"])
    activity_data["type"] = pd.Categorical(activity_data["type"])
    activity_data = activity_data.convert_dtypes()

    researches = pd.read_csv(data_path / "researches.csv", usecols=["id", "user"])
    researches = researches.rename(columns={"id": "research_id"})
    researches = researches.convert_dtypes()

    raw_data = pd.merge(activity_data, researches, on="research_id")
    raw_data = raw_data[raw_data["user"] != 20]

    actions = raw_data[raw_data["type"] == "Action"]
    actions["info"] = actions["info"].apply(_normalize_info)

    shortcuts = raw_data[raw_data["type"] == "Shortcut"]

    shortcut_actions = pd.merge(
        actions.reset_index(),  # To preserve the index
        shortcuts[["research_id", "action_id"]],
        on=["research_id", "action_id"],
    ).set_index("index")

    if kind == "all":
        data = actions
    elif kind == "shortcut":
        data = shortcut_actions
    elif kind == "standalone":
        data = actions[~actions.index.isin(shortcut_actions.index)]
    else:
        raise ValueError(f"Invalid value for `kind`: {kind}")

    return data[["user", "info"]]


def show_top_actions_page():
    if st.session_state.get("data_path") is None:
        st.error(f"You can't access this page without passing data.")
        st.stop()

    data_path = st.session_state["data_path"]

    # ------------------------------------------------------------------------

    st.title("Top Actions")

    with st.expander("Config", expanded=True):
        left, right = st.columns(2, vertical_alignment="center")

        with left:
            kind = st.radio(
                "Kind",
                ["all", "shortcut", "standalone"],
                horizontal=True,
                index=1,
                format_func=str.title,
            )

        shortcuts_data = load_data(data_path, kind=kind)

        with right:
            top = st.number_input("Top", value=10, min_value=1, max_value=len(shortcuts_data))

        with left:
            normalize = st.toggle("Normalize", value=True)

        with right:
            ascending = st.toggle("Ascending")

        stats = shortcuts_data.groupby("user")["info"].unique().explode().value_counts(ascending=ascending)

        if normalize:
            stats /= shortcuts_data["user"].nunique()
            stats *= 100

        stats = stats.reset_index(drop=False)

        st.divider()

        filter_mode = st.radio("Filter Mode", ["Exclude", "Include"], horizontal=True)

        select = st.multiselect("Filter", stats["info"].unique())

        if select:
            mask = stats["info"].isin(select)

            if filter_mode == "Exclude":
                stats = stats[~mask]
            else:
                stats = stats[mask]

        stats = stats.head(top)

    fig = px.bar(stats.reset_index(), x="info", y="count")

    fig.update_xaxes(title="Action")
    fig.update_yaxes(title="Number of Users" + (" (%)" if normalize else ""))

    st.plotly_chart(fig)
