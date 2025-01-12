import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from dbsetup import setupDB
from utils import clean_text


def create_streamlit_app(llm, portfolio, clean_text):
    # Set up the page
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    st.title("📧 Cold Mail Generator")

    # Input Section
    st.markdown("### Enter Job Page URL")
    url_input = st.text_input(
        "Paste the URL of the careers page or job listing below:",
        placeholder="e.g., https://jobs.nike.com/job/R-48491...",
    )
    st.markdown("---")
    
    # Button for submission
    col1, col2 = st.columns([2, 1])
    with col1:
        submit_button = st.button("Generate Email", type="primary")
    with col2:
        st.write("")  # Add spacing
    
    # Output Section
    if submit_button:
        if url_input.strip() == "":
            st.error("Please provide a valid URL.")
        else:
            with st.spinner("Processing the URL... Please wait."):
                try:
                    # Load data from the provided URL
                    loader = WebBaseLoader([url_input])
                    raw_data = loader.load().pop().page_content
                    cleaned_data = clean_text(raw_data)

                    # Load portfolio and extract jobs
                    portfolio.load_portfolio()
                    jobs = llm.extract_jobs(cleaned_data)

                    if not jobs:
                        st.warning("No job descriptions were found on the provided URL.")
                    else:
                        for idx, job in enumerate(jobs):
                            st.markdown(f"#### Job {idx + 1}: {job.get('title', 'Unknown Position')}")
                            st.write("**Description:**", job.get('description', 'No description provided.'))

                            # Get skills and query portfolio links
                            skills = job.get("skills", [])
                            links = portfolio.query_links(skills)

                            # Generate the email
                            email = llm.write_mail(job, links)
                            st.markdown("##### Generated Email:")
                            st.code(email, language="markdown")
                            st.markdown("---")
                except Exception as e:
                    st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = setupDB()
    create_streamlit_app(chain, portfolio, clean_text)
