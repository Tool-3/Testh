import streamlit as st
import pandas as pd
import pdfplumber
import io

def extract_text_from_all_pages(pdf):
    text = ""
    with pdfplumber.open(pdf) as pdf_file:
        for page in pdf_file.pages:
            text += page.extract_text() + "\n"
    return text

def convert_text_to_dataframe(text):
    lines = text.split('\n')
    data = [line.split() for line in lines if line.strip()]  # Skip empty lines
    return pd.DataFrame(data)

def main():
    st.title("PDF to CSV Converter")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        text = extract_text_from_all_pages(uploaded_file)
        st.text_area("Extracted Text", text, height=300)
        
        if st.button("Convert to CSV"):
            df = convert_text_to_dataframe(text)
            st.dataframe(df)
            
            # Convert DataFrame to CSV and store it in a binary buffer
            csv_buffer = io.BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            st.download_button(
                label="Download CSV",
                data=csv_buffer,
                file_name="output.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
