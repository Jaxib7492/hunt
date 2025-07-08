import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os

# -------- Google Sheets Setup --------
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1Bu8mzwoJUXw3JAD63nmTcmAlYo9GdR9vQyzGkukTWgA"
SHEET_NAME = "Outreach Data"  # Your worksheet/tab name

@st.cache_resource(ttl=3600)
def get_gsheet_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    return client

# -------- File-based Name Persistence --------
def load_saved_name():
    if os.path.exists("name_store.txt"):
        with open("name_store.txt", "r") as f:
            return f.read().strip()
    return ""

def save_name_to_file(name):
    with open("name_store.txt", "w") as f:
        f.write(name)

# -------- Google Sheet Row & Entry Logic --------
def find_next_empty_bcf_row(sheet):
    """Find the first row where columns B, C, and F are all empty."""
    data = sheet.get_all_values()
    for idx, row in enumerate(data, start=1):
        b = row[1] if len(row) > 1 else ""
        c = row[2] if len(row) > 2 else ""
        f = row[5] if len(row) > 5 else ""
        if not b and not c and not f:
            return idx
    return len(data) + 1

def save_reference_entry(name, contact, reference):
    client = get_gsheet_client()
    sheet = client.open_by_url(GSHEET_URL).worksheet(SHEET_NAME)

    next_row = find_next_empty_bcf_row(sheet)

    if next_row > sheet.row_count:
        sheet.add_rows(100)

    # Write to Columns B (2), C (3), F (6)
    sheet.update_cell(next_row, 2, name)
    sheet.update_cell(next_row, 3, contact)
    sheet.update_cell(next_row, 6, reference)

# -------- Streamlit App UI --------
def main():
    st.set_page_config(page_title="Reference Entry", layout="centered")
    st.title("📋 Submit Your Reference")

    # Sidebar: Name input (persistent)
    st.sidebar.header("👤 Your Name")
    if "name" not in st.session_state:
        st.session_state.name = load_saved_name()

    new_name = st.sidebar.text_input("Enter your name once", value=st.session_state.name)

    if new_name != st.session_state.name:
        st.session_state.name = new_name
        save_name_to_file(new_name)

    # Main Form
    st.subheader("✉️ Contact & Reference Info")
    with st.form("reference_form"):
        contact = st.text_input("Email / Contact Info")
        reference = st.text_area("Reference")
        submitted = st.form_submit_button("✅ Submit")

        if submitted:
            if not st.session_state.name:
                st.warning("⚠️ Please enter your name from the sidebar.")
            elif not contact or not reference:
                st.warning("⚠️ Please fill in both Contact and Reference fields.")
            else:
                try:
                    save_reference_entry(st.session_state.name, contact, reference)
                    st.success("✅ Entry submitted successfully!")
                except Exception as e:
                    st.error("❌ Failed to submit entry:")
                    st.exception(e)

if __name__ == "__main__":
    main()
