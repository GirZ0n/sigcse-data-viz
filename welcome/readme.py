import streamlit as st


def show_readme_page():
    st.title("KOALA Visualization")

    st.header("🔍 Overview")

    st.markdown(
        """
        This app provides a visualization of KOALA data, offering insights into user behavior based.
        The main features include basic user session statistics, top user actions,
        top windows used, and window focus time analysis.
        """
    )

    st.header("📈 Features")

    st.subheader("📌 Basic Statistics")

    st.markdown(
        """
        * 👥 Total users (participating in the study)
        * 🔄 Total sessions (within KOALA)
        * 📊 Median sessions per user
        * ⏳ Session/study duration: minimum, median and maximum
        """
    )

    st.subheader("🎯 Top Actions")

    st.markdown(
        """
        * 📊 A chart showing how many users triggered specific actions
        * 🛠 Filters available:
            * 🔍 Show all actions
            * ⌨️ Show actions triggered via shortcuts
            * 🖱 Show actions triggered via the UI
        * 🔝 Configurable top actions list (default: top 10)
        * 📏 Normalize data (divide by the total number of users)
        * 🔼🔽 Sort the chart in ascending order (default: descending)
        * ⚙️ Filter relevant or irrelevant actions
        """
    )

    st.subheader("🪟 Top Windows")

    st.markdown(
        """
        * 📊 A chart showing how many users interacted with specific windows
        * 🔝 Configurable top windows list (default: top 10)
        * 📏 Normalize data (divide by the total number of users)
        * 🔼🔽 Sort the chart in ascending order (default: descending)
        * ⚙️ Filter relevant or irrelevant windows
        """
    )

    st.subheader("⏳ Window Focus Time")

    st.markdown(
        """
        * 📊 Box plot displaying total time spent on each window
        * 🔝 Configurable top windows list (default: top 10)
        * ⏳ Adjustable time scale: seconds, minutes, hours (default: seconds)
        * 🔼🔽 Sort the chart in ascending order (default: descending)
        * ⚙️ Filter relevant or irrelevant windows
        """
    )
