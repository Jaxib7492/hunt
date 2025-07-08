import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --------- CONFIG ---------
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1Bu8mzwoJUXw3JAD63nmTcmAlYo9GdR9vQyzGkukTWgA"
SHEET_NAME = "Outreach Data"

# --------- GOOGLE SHEETS AUTH ---------
@st.cache_resource
def get_gsheet_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    return gspread.authorize(creds)

# --------- SHEET UTILITY ---------
def get_next_available_row(sheet, col_letter):
    col_values = sheet.col_values(ord(col_letter.upper()) - 64)
    return len(col_values) + 1

def email_exists(sheet, email):
    emails = sheet.col_values(3)  # Column C is index 3
    return email.strip().lower() in (e.strip().lower() for e in emails)

def save_reference_entry(name, email, reference):
    client = get_gsheet_client()
    sheet = client.open_by_url(GSHEET_URL).worksheet(SHEET_NAME)

    if email_exists(sheet, email):
        st.error("❌ This email already exists in the sheet.")
        return False

    row = get_next_available_row(sheet, 'C')  # Based on email column
    sheet.update_cell(row, 2, name)       # Column B
    sheet.update_cell(row, 3, email)      # Column C
    sheet.update_cell(row, 6, reference)  # Column F

    return True

# --------- STREAMLIT UI ---------
def main():
    st.title("📋 Quick Contact Entry App")

    # ----- NAME SETTING (SIDEBAR) -----
    st.sidebar.header("Your Name (Saved Locally)")
    if "name" not in st.session_state:
        st.session_state.name = ""

    st.session_state.name = st.sidebar.text_input("Enter your name", st.session_state.name)

    # ----- FORM -----
    st.subheader("➕ Add New Contact")
    with st.form("entry_form"):
        email = st.text_input("Contact Email / Info")
        reference = st.text_input("Reference (Who referred or context?)")
        submitted = st.form_submit_button("Submit Entry")

        if submitted:
            if st.session_state.name.strip() == "":
                st.warning("⚠️ Please enter your name in the sidebar first.")
            elif email.strip() == "":
                st.warning("⚠️ Email/Contact cannot be empty.")
            else:
                success = save_reference_entry(st.session_state.name.strip(), email.strip(), reference.strip())
                if success:
                    st.success("✅ Entry submitted successfully!")
                    # Clear input fields but retain name
                    st.experimental_set_query_params()
                    st.rerun()

if __name__ == "__main__":
    main()
