import streamlit as st
import pandas as pd
from src.utils import parse_kindle_html, generate_markdown
import io

def main():
    st.set_page_config(
        page_title="Kindle Notes Processor",
        page_icon="📚",
        layout="wide"
    )

    st.title("📚 Kindle Notes Processor")
    
    st.markdown("""
    ### Instructions
    1. **Upload** your Kindle highlights HTML export file (usually named something like `Notebook.html`).
    2. The app will **extract** highlights and your custom notes.
    3. Processed notes will be displayed below as **Markdown** and will be available for **download**.
    """)

    uploaded_file = st.file_uploader("Upload Kindle Highlights HTML", type=["html"])

    html_content = None
    if uploaded_file is not None:
        html_content = uploaded_file.getvalue().decode("utf-8")
    else:
        # Fallback to local file for development/preview
        try:
            with open("sample.html", "r", encoding="utf-8") as f:
                html_content = f.read()
                st.info("Showing results for local file: `Flow-Notebook.html`")
        except FileNotFoundError:
            pass

    if html_content is not None:
        try:
            # Process content
            with st.spinner("Processing highlights..."):
                df, metadata = parse_kindle_html(html_content)
            
            if df.empty:
                st.warning("No highlights or notes found in the uploaded file.")
                return

            st.success(f"Successfully processed highlights for: **{metadata['title']}** by {metadata['author']}")

            # Generate Markdown
            markdown_text = generate_markdown(df, metadata)

            # UI Layout for results
            # col1, col2 = st.columns([1, 1])

            # with col1:
            #     st.subheader("Markdown Preview")
            #     st.markdown(markdown_text)

            # with col2:
            #     st.subheader("Raw Markdown & Download")
            #     st.code(markdown_text, language="markdown")
                
            #     # Download button
            #     file_name = f"{metadata['title'].replace(' ', '_')}_notes.md"
            #     st.download_button(
            #         label="Download Markdown (.md)",
            #         data=markdown_text,
            #         file_name=file_name,
            #         mime="text/markdown"
            #     )

            # Show raw data optionally
            
            st.dataframe(df)

        except Exception as e:
            st.error(f"An error occurred while processing the file: {str(e)}")
            st.info("Please ensure you are uploading a valid Kindle export HTML file.")

if __name__ == "__main__":
    main()
