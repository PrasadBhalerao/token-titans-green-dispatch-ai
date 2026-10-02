import streamlit as st

from src.core.data_loader import DatasetValidationError
from src.core.data_loader import load_dataset
from src.ui.dashboard import render_dashboard


def main() -> None:
    st.set_page_config(
        page_title="GreenDispatch AI",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    try:
        dataset = load_dataset()
        render_dashboard(dataset)
    except DatasetValidationError as exc:
        st.error(f"Dataset validation failed: {exc}")
    except Exception as exc:
        st.error(f"Unable to start GreenDispatch AI: {exc}")


if __name__ == "__main__":
    main()
