import streamlit as st
from streamlit_gsheets import GSheetsConnection
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

def show_main_page():
    if st.session_state.get("logged_in") and st.session_state.get("is_admin"):
        st.title("Google Sheet Data Display")

        # Establish connection to Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Read data from the specified worksheet and columns
        df = conn.read(worksheet="Sheet2", usecols=[0, 1, 2, 3, 4, 5, 6], ttl=5)

        # Drop any rows where all elements are NaN
        df = df.dropna(how="all")

        # Display the data frame in Streamlit
        st.dataframe(df, hide_index=True)

        st.write("### Add Your Information")

        # Define options for selectboxes
        time_options = ["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM",
                        "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM",
                        "05:00 PM", "05:30 PM", "06:00 PM"]
        service_options = ["nail job", "Hair trim", "Make up", "Hair job", "Manicure", 'Pedicure', "Hair dye", "Perm"]

        with st.form("entry_form"):
            name = st.text_input("Name")
            surname = st.text_input("Surname")
            phone_number = st.text_input("Phone Number")
            reservation_date = st.date_input("Reservation Date", datetime.today())
            reservation_time = st.selectbox("Reservation Time", time_options)
            inquired_service = st.selectbox("Inquired Service", service_options)
            submitted = st.form_submit_button("Submit")

            if submitted:
                # Calculate the next ID
                try:
                    # Load secrets from the Streamlit secrets management
                    gsheets_secrets = st.secrets["connections"]["gsheets"]

                    # Define the scope
                    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

                    # Create credentials object from the secrets
                    credentials = Credentials.from_service_account_info(gsheets_secrets, scopes=scope)

                    # Authorize the client
                    client = gspread.authorize(credentials)

                    # Open the sheet
                    sheet = client.open_by_url(gsheets_secrets["spreadsheet"]).worksheet("Sheet2")

                    # Get the current data
                    current_data = sheet.get_all_values()

                    # Determine the next ID based on the length of the current data
                    if len(current_data) > 1:
                        last_id = int(current_data[-1][0])
                        next_id = last_id + 1
                    else:
                        next_id = 1

                    # Prepare the row to be added
                    new_row = [next_id, name, surname, phone_number, str(reservation_date), reservation_time, inquired_service]

                    # Append the new row
                    sheet.append_row(new_row)
                    st.success(f"Information added successfully with ID {next_id}!")
                except Exception as e:
                    st.error(f"Error adding information: {e}")

        st.write("### Remove a Row by ID")

        with st.form("delete_form"):
            id_to_delete = st.text_input("Enter ID to delete")
            delete_submitted = st.form_submit_button("Delete Row")

            if delete_submitted:
                try:
                    # Load secrets from the Streamlit secrets management
                    gsheets_secrets = st.secrets["connections"]["gsheets"]

                    # Define the scope
                    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

                    # Create credentials object from the secrets
                    credentials = Credentials.from_service_account_info(gsheets_secrets, scopes=scope)

                    # Authorize the client
                    client = gspread.authorize(credentials)

                    # Open the sheet
                    sheet = client.open_by_url(gsheets_secrets["spreadsheet"]).worksheet("Sheet2")

                    # Find the row with the specified ID
                    cell = sheet.find(id_to_delete, in_column=1)  # Assuming IDs are in the first column
                    if cell:
                        sheet.delete_row(cell.row)
                        st.success(f"Row with ID {id_to_delete} deleted successfully!")
                    else:
                        st.error(f"ID {id_to_delete} not found!")
                except Exception as e:
                    st.error(f"Error deleting row: {e}")

        st.write("### Edit a Row by ID")

        edit_id = st.text_input("Enter ID to edit")
        load_data = st.button("Load Data")

        if load_data:
            try:
                # Load secrets from the Streamlit secrets management
                gsheets_secrets = st.secrets["connections"]["gsheets"]

                # Define the scope
                scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

                # Create credentials object from the secrets
                credentials = Credentials.from_service_account_info(gsheets_secrets, scopes=scope)

                # Authorize the client
                client = gspread.authorize(credentials)

                # Open the sheet
                sheet = client.open_by_url(gsheets_secrets["spreadsheet"]).worksheet("Sheet2")

                # Find the row with the specified ID
                cell = sheet.find(edit_id, in_column=1)  # Assuming IDs are in the first column
                if cell:
                    row_data = sheet.row_values(cell.row)
                    st.session_state.edit_id = edit_id
                    st.session_state.edit_row = cell.row
                    st.session_state.edit_data = row_data
                    st.success(f"Data for ID {edit_id} loaded successfully!")
                else:
                    st.error(f"ID {edit_id} not found!")
            except Exception as e:
                st.error(f"Error loading data: {e}")

        if "edit_data" in st.session_state:
            with st.form("edit_form"):
                edit_name = st.text_input("Edit Name", st.session_state.edit_data[1])
                edit_surname = st.text_input("Edit Surname", st.session_state.edit_data[2])
                edit_phone_number = st.text_input("Edit Phone Number", st.session_state.edit_data[3])
                try:
                    edit_reservation_date = datetime.strptime(st.session_state.edit_data[4], "%Y-%m-%d").date()
                except ValueError:
                    edit_reservation_date = datetime.today().date()
                edit_reservation_date = st.date_input("Edit Reservation Date", edit_reservation_date)
                edit_reservation_time = st.selectbox("Edit Reservation Time", time_options, index=time_options.index(st.session_state.edit_data[5]))
                edit_inquired_service = st.selectbox("Edit Inquired Service", service_options, index=service_options.index(st.session_state.edit_data[6]))
                edit_submitted = st.form_submit_button("Update Row")

                if edit_submitted:
                    try:
                        # Load secrets from the Streamlit secrets management
                        gsheets_secrets = st.secrets["connections"]["gsheets"]

                        # Define the scope
                        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

                        # Create credentials object from the secrets
                        credentials = Credentials.from_service_account_info(gsheets_secrets, scopes=scope)

                        # Authorize the client
                        client = gspread.authorize(credentials)

                        # Open the sheet
                        sheet = client.open_by_url(gsheets_secrets["spreadsheet"]).worksheet("Sheet2")

                        # Update the row with the specified ID
                        updated_row = [st.session_state.edit_id, edit_name, edit_surname, edit_phone_number, str(edit_reservation_date), edit_reservation_time, edit_inquired_service]
                        sheet.update(f'A{st.session_state.edit_row}:G{st.session_state.edit_row}', [updated_row])
                        st.success(f"Row with ID {st.session_state.edit_id} updated successfully!")
                    except Exception as e:
                        st.error(f"Error updating row: {e}")
    else:
        st.warning("You are not authorized to view this page. Please log in as admin.")

# Call the function to display the main page
show_main_page()
