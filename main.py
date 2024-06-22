import streamlit as st
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, time

def show_main_page():
    if st.session_state.get("logged_in") and st.session_state.get("is_admin"):
        st.title("Google Sheet Data Display")

        # Establish connection to Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Read data from the specified worksheet and columns
        df = conn.read(worksheet="Sheet2", usecols=[0, 1, 2, 3, 4, 5, 6], ttl=5)

        # Drop any rows where all elements are NaN
        df = df.dropna(how="all")

        # Assuming actual column names based on the provided info
        reservation_date_col = 'reservation date'
        reservation_time_col = 'reservation time'
        inquired_service_col = 'inquired service'

        # Convert date and time columns to editable formats
        df[reservation_date_col] = df[reservation_date_col].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date() if x else datetime.today().date())

        def parse_time(time_str):
            time_str = time_str.strip()
            if 'PM' in time_str or 'AM' in time_str:
                try:
                    # Try parsing 12-hour format
                    return datetime.strptime(time_str, '%I:%M %p').time()
                except ValueError:
                    # Handle malformed 12-hour format
                    return datetime.strptime(time_str.replace('PM', '').replace('AM', '').strip(), '%H:%M').time()
            else:
                # Handle 24-hour format
                return datetime.strptime(time_str, '%H:%M').time()

        df[reservation_time_col] = df[reservation_time_col].apply(lambda x: parse_time(x) if x else time(9, 0))

        # Define service options
        service_options = ["nail job", "Hair trim", "Make up", "Hair job", "Manicure", 'Pedicure', "Hair dye", "Perm"]

        # Create a dictionary to map the current values to the selection options
        service_options_dict = {service: service for service in service_options}

        # Replace current values in the 'inquired service' column with the selection options
        df[inquired_service_col] = df[inquired_service_col].map(service_options_dict).fillna(df[inquired_service_col])

        # Create options for time input
        time_options = [time(hour, minute).strftime('%I:%M %p') for hour in range(9, 19) for minute in [0, 30]]

        # Display the data frame in Streamlit using data_editor
        edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", hide_index=True)

        # When the data is edited, save the changes back to Google Sheets
        if st.button("Save Changes"):
            try:
                # Save changes back to Google Sheets using GSheetsConnection
                conn.write(worksheet="Sheet2", df=edited_df)
                st.success("Changes saved successfully!")
            except Exception as e:
                st.error(f"Error saving changes: {e}")

        st.write("### Remove a Row by ID")

        with st.form("delete_form"):
            id_to_delete = st.text_input("Enter ID to delete")
            delete_submitted = st.form_submit_button("Delete Row")

            if delete_submitted:
                try:
                    # Find and delete the row with the specified ID
                    edited_df = edited_df[edited_df['ID'] != id_to_delete]
                    conn.write(worksheet="Sheet2", df=edited_df)
                    st.success(f"Row with ID {id_to_delete} deleted successfully!")
                except Exception as e:
                    st.error(f"Error deleting row: {e}")

    else:
        st.warning("You are not authorized to view this page. Please log in as admin.")

# Call the function to display the main page
show_main_page()
