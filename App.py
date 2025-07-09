import streamlit as st
import gspread
from google.oauth2 import service_account
from datetime import datetime

# -------- Google Sheets Setup --------
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1Bu8mzwoJUXw3JAD63nmTcmAlYo9GdR9vQyzGkukTWgA"
SHEET_NAME = "Outreach Data"

scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scopes
)
client = gspread.authorize(creds)

def save_reference_entry(name, email, reference):
    sheet = client.open_by_url(GSHEET_URL).worksheet(SHEET_NAME)
    data = sheet.get_all_values()

    existing_emails = [row[2].strip().lower() for row in data if len(row) > 2]
    if email.strip().lower() in existing_emails:
        st.error("❌ This email already exists in the sheet.")
        return False

    next_row = None
    for i, row in enumerate(data[1:], start=2):
        b_empty = len(row) <= 1 or row[1].strip() == ""
        c_empty = len(row) <= 2 or row[2].strip() == ""
        f_empty = len(row) <= 5 or row[5].strip() == ""
        if b_empty and c_empty and f_empty:
            next_row = i
            break

    if not next_row:
        next_row = len(data) + 1

    today_str = datetime.now().strftime("%Y-%m-%d")
    sheet.update_cell(next_row, 2, name)       # Column B
    sheet.update_cell(next_row, 3, email)      # Column C
    sheet.update_cell(next_row, 6, reference)  # Column F
    sheet.update_cell(next_row, 7, today_str)  # Column G

    return True

def count_user_today_entries(name):
    sheet = client.open_by_url(GSHEET_URL).worksheet(SHEET_NAME)
    data = sheet.get_all_values()
    today_str = datetime.now().strftime("%Y-%m-%d")

    count = 0
    for row in data[1:]:
        if len(row) > 6:
            row_name = row[1].strip().lower()
            row_date = row[6].strip()
            if row_name == name.strip().lower() and row_date == today_str:
                count += 1
    return count

def main():
    st.set_page_config(page_title="Outreach Submission Form")
    st.title("📋 Outreach Submission Form")

    saved_name = st.query_params.get("name", "")
    
    with st.form("entry_form"):
        name = st.text_input("👤 Your Name", value=saved_name)
        contact = st.text_input("📧 Client Email")
        reference = st.text_area("📝 Reference Message")

        submitted = st.form_submit_button("Submit")

        if submitted:
            if not name or not contact or not reference:
                st.warning("⚠️ Please fill in all fields.")
            else:
                st.query_params["name"] = name
                success = save_reference_entry(name, contact, reference)
                if success:
                    st.success("✅ Entry submitted successfully!")

    # ✅ Show only current user's entry count in sidebar
    if saved_name or name:
        current_user = name if name else saved_name
        user_count = count_user_today_entries(current_user)
        st.sidebar.markdown("### 📊 Your Submissions Today:")
        st.sidebar.markdown(f"- **{current_user}**: `{user_count}`")

if __name__ == "__main__":
    main()
