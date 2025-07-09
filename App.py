import streamlit as st
import gspread
from google.oauth2 import service_account
import os

# -------- Google Sheets Setup --------
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1Bu8mzwoJUXw3JAD63nmTcmAlYo9GdR9vQyzGkukTWgA"
SHEET_NAME = "Outreach Data"

# Authenticate using credentials stored in .streamlit/secrets.toml
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)
client = gspread.authorize(creds)

# -------- Persistent Name Store --------
NAME_FILE = "name_store.txt"

def load_saved_name():
    if os.path.exists(NAME_FILE):
        with open(NAME_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def save_name(name):
    with open(NAME_FILE, "w", encoding="utf-8") as f:
        f.write(name)

# -------- Entry Saving --------
def save_reference_entry(name, email, reference):
    sheet = client.open_by_url(GSHEET_URL).worksheet(SHEET_NAME)
    data = sheet.get_all_values()

    # Check for duplicate email in column C (index 2)
    existing_emails = [row[2].strip().lower() for row in data if len(row) > 2]
    if email.strip().lower() in existing_emails:
        st.error("❌ This email already exists in the sheet.")
        return False

    # Find the next empty row
    next_row = None
    for i, row in enumerate(data[1:], start=2):  # Skip header row
        b_empty = len(row) <= 1 or row[1].strip() == ""
        c_empty = len(row) <= 2 or row[2].strip() == ""
        f_empty = len(row) <= 5 or row[5].strip() == ""
        if b_empty and c_empty and f_empty:
            next_row = i
            break

    if not next_row:
        next_row = len(data) + 1

    # Update sheet
    sheet.update_cell(next_row, 2, name)      # Column B
    sheet.update_cell(next_row, 3, email)     # Column C
    sheet.update_cell(next_row, 6, reference) # Column F

    return True

# -------- Streamlit UI --------
def main():
    st.set_page_config(page_title="Outreach Entry Form")
    st.title("📋 Outreach Submission Form")

    # Load and pre-fill name
    saved_name = load_saved_name()

    # Use session state for name (makes editable + persistent behavior)
    if "name_input" not in st.session_state:
        st.session_state["name_input"] = saved_name

    with st.form("entry_form"):
        name = st.text_input("👤 Your Name", value=st.session_state["name_input"], key="name_input")
        contact = st.text_input("📧 Client Email", key="contact")
        reference = st.text_area("📝 Reference Message", key="reference")

        submitted = st.form_submit_button("Submit")

        if submitted:
            if not name or not contact or not reference:
                st.warning("⚠️ Please fill in all fields.")
            else:
                # Save name only if changed
                if name != saved_name:
                    save_name(name)

                success = save_reference_entry(name, contact, reference)
                if success:
                    st.success("✅ Entry submitted successfully!")

                    # Clear fields except name
                    st.session_state["contact"] = ""
                    st.session_state["reference"] = ""

# Run app
if __name__ == "__main__":
    main()
