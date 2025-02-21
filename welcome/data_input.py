import os
from pathlib import Path
from typing import Literal

import pandas as pd
import streamlit as st

REQUIRED_FILES = (
    "activitydata.csv",
    "researches.csv",
    "toolwindowdata.csv",
)


def _format_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.2f} sec"
    elif seconds < 3600:
        return f"{seconds / 60:.2f} min"
    elif seconds < 86400:
        return f"{seconds / 3600:.2f} hr"
    else:
        return f"{seconds / 86400:.2f} days"


@st.cache_data(show_spinner='Calculating basic stats...')
def _calculate_basic_research_stats(data_path: Path) -> tuple[int, int, float]:
    research_data = pd.read_csv(data_path / "researches.csv")
    research_data = research_data[research_data["user"] != 20]
    return research_data["user"].nunique(), research_data["id"].nunique(), research_data.groupby("user").size().median()


@st.cache_data(show_spinner='Calculating duration stats...')
def _calculate_duration_stats(data_path: Path, per: Literal["user", "session"]) -> tuple[float, float, float]:
    activitydata = pd.read_csv(data_path / "activitydata.csv", usecols=["research_id", "date"])
    document_data = pd.read_csv(data_path / "documentdata.csv", usecols=["research_id", "date"])
    fileeditordata = pd.read_csv(data_path / "fileeditordata.csv", usecols=["research_id", "date"])
    surveydata = pd.read_csv(data_path / "surveydata.csv", usecols=["research_id", "date"])
    toolwindowdata = pd.read_csv(data_path / "toolwindowdata.csv", usecols=["research_id", "date"])

    data = pd.concat([activitydata, document_data, fileeditordata, surveydata, toolwindowdata])

    researches = pd.read_csv(data_path / "researches.csv", usecols=["id", "user"])
    data = pd.merge(data, researches, left_on="research_id", right_on="id", how="left")[["research_id", "user", "date"]]

    data = data[data["user"] != 20]
    data["date"] = pd.to_datetime(data["date"], format="mixed")
    data = data.reset_index(drop=True)
    data.convert_dtypes()

    if per == "user":
        groupby = "user"
    elif per == "session":
        groupby = "research_id"
    else:
        raise ValueError(f"Invalid value for `per`: {per}")

    duration = data.groupby(groupby)["date"].apply(lambda x: (x.max() - x.min()).total_seconds())

    return duration.min(), duration.median(), duration.max()


def show_data_input_page():
    st.title("Data Input")

    data_path = st.text_input("Data path:", value=st.session_state.get("data_path"))

    if data_path is None:
        st.stop()

    data_path = Path(data_path)

    if not data_path.exists():
        st.error("The specified path does not exist.")
        st.stop()

    if not data_path.is_dir():
        st.error(f"The specified path must be a directory. You should enter a path to a folder with research data.")
        st.stop()

    files = os.listdir(data_path)
    missing_file = next((required_file for required_file in REQUIRED_FILES if required_file not in files), None)
    if missing_file is not None:
        st.error(f"The directory must contain `{missing_file}`.")
        st.stop()

    st.session_state["data_path"] = data_path
    st.success("The data has been successfully loaded. Now you can access pages with different analyses.")

    st.header("Basic stats")

    number_of_users, number_of_sessions, median_number_of_sessions = _calculate_basic_research_stats(data_path)

    left, middle, right = st.columns(3)

    with left:
        st.metric("Number of users", number_of_users)

    with middle:
        st.metric("Number of sessions", number_of_sessions)

    with right:
        st.metric("Median number of sessions", round(median_number_of_sessions, 2))

    session_min, session_median, session_max = _calculate_duration_stats(data_path, per="session")

    left, middle, right = st.columns(3)

    with left:
        st.metric("Minimum session duration", _format_time(session_min))

    with middle:
        st.metric("Median session duration", _format_time(session_median))

    with right:
        st.metric("Maximum session duration", _format_time(session_max))

    user_min, user_median, user_max = _calculate_duration_stats(data_path, per="user")

    left, middle, right = st.columns(3)

    with left:
        st.metric("Minimum research duration", _format_time(user_min))

    with middle:
        st.metric("Median research duration", _format_time(user_median))

    with right:
        st.metric("Maximum research duration", _format_time(user_max))
