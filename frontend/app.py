import streamlit as st
import requests
from pathlib import Path

ASSETS_PATH = Path(__file__).absolute().parents[1] / "assets"

def layout():
    st.markdown("# ItalyTravels 🇮🇹")
    st.markdown("Ask a question about top 5 Italian Cities")
    text_input = st.text_input(label="Ask a question")

    if st.button("Send") and text_input != "":
        response = requests.post(
            "http://127.0.0.1:8000/rag/query",
            json={"prompt": text_input}
        )

        if response.status_code != 200:
            st.error(f"Something went wrong: {response.json().get('detail', 'Unknown error')}. Please try again.")
        else:
            data = response.json()

            st.markdown("## Question:")
            st.markdown(text_input)

            st.markdown("## Answer:")
            st.markdown(data["answer"])

            st.markdown("## Source:")
            st.markdown(data["filepath"])

            st.image(ASSETS_PATH / f"{data['filename']}.jpg")

if __name__ == "__main__":
    layout()