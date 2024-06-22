import streamlit as st

def show_home_page():
    st.title("Welcome to the Home Page")

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if "is_admin" not in st.session_state:
        st.session_state["is_admin"] = False

    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login Section")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == "admin" and password == "admin":  # Simple validation
                st.success("Logged In as {}".format(username))
                st.session_state["logged_in"] = True
                st.session_state["is_admin"] = True
                st.experimental_rerun()  # Refresh the page to update the state
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "Sign Up":
        st.subheader("Create New Account")

        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            st.success("Account created successfully for {}".format(new_user))
            st.info("Go to the Login Menu to login")

# Call the function to display the home page
show_home_page()
