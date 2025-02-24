import zipfile
from collections import namedtuple
from typing import Literal

import pandas as pd
import streamlit as st

ZipData = namedtuple(
    "ZipData",
    ["researches", "activitydata", "toolwindowdata", "documentdata", "fileeditordata", "surveydata"],
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


@st.cache_data(show_spinner="Calculating basic stats...")
def _calculate_basic_research_stats(zip_data: ZipData) -> tuple[int, int, float]:
    researches_data = zip_data.researches
    researches_data = researches_data[researches_data["user"] != 20]

    return (
        researches_data["user"].nunique(),
        researches_data["id"].nunique(),
        researches_data.groupby("user").size().median(),
    )


@st.cache_data(show_spinner="Calculating duration stats...")
def _calculate_duration_stats(zip_data: ZipData, per: Literal["user", "session"]) -> tuple[float, float, float]:
    activity_data = zip_data.activitydata[["research_id", "date"]]
    document_data = zip_data.documentdata[["research_id", "date"]]
    file_editor_data = zip_data.fileeditordata[["research_id", "date"]]
    survey_data = zip_data.surveydata[["research_id", "date"]]
    tool_window_data = zip_data.toolwindowdata[["research_id", "date"]]

    data = pd.concat([activity_data, document_data, file_editor_data, survey_data, tool_window_data])

    researches = zip_data.researches[["id", "user"]]
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


def check_zip_file(zip_file):
    if not zipfile.is_zipfile(zip_file):
        st.error("The passed file is not a valid zip file.")
        st.stop()

    with zipfile.ZipFile(zip_file) as zip_ref:
        files = zip_ref.namelist()

        missing_file = next(
            (required_file for required_file in ZipData._fields if f"{required_file}.csv" not in files),
            None,
        )

        if missing_file is not None:
            st.error(f"The zip must contain `{missing_file}.csv`.")
            st.stop()

        data = {}
        for file_name in ZipData._fields:
            with zip_ref.open(f"{file_name}.csv") as file:
                data[file_name] = pd.read_csv(file)

    return ZipData(**data)


def load_data() -> ZipData:
    zip_file = st.file_uploader("Data:", type="zip")

    if zip_file is not None:
        zip_data = check_zip_file(zip_file)
    elif (zip_data := st.session_state.get("zip_data")) is None:
        st.stop()

    st.session_state["zip_data"] = zip_data
    st.success("The data has been successfully loaded. Now you can access pages with different analyses.")

    return zip_data


def show_data_input_page():
    st.title("Data Input")

    zip_data = load_data()

    st.header("Basic stats")

    number_of_users, number_of_sessions, median_number_of_sessions = _calculate_basic_research_stats(zip_data)

    left, middle, right = st.columns(3)

    with left:
        st.metric("Number of users", number_of_users)

    with middle:
        st.metric("Number of sessions", number_of_sessions)

    with right:
        st.metric("Median number of sessions", round(median_number_of_sessions, 2))

    session_min, session_median, session_max = _calculate_duration_stats(zip_data, per="session")

    left, middle, right = st.columns(3)

    with left:
        st.metric("Minimum session duration", _format_time(session_min))

    with middle:
        st.metric("Median session duration", _format_time(session_median))

    with right:
        st.metric("Maximum session duration", _format_time(session_max))

    user_min, user_median, user_max = _calculate_duration_stats(zip_data, per="user")

    left, middle, right = st.columns(3)

    with left:
        st.metric("Minimum research duration", _format_time(user_min))

    with middle:
        st.metric("Median research duration", _format_time(user_median))

    with right:
        st.metric("Maximum research duration", _format_time(user_max))
