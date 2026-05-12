import streamlit as st
from db_queries import *
from chatbot_vector_embedding import chatbot

conn = get_connection()

st.set_page_config(page_title="HR Dashboard", layout="wide")
st.title("🏢 HR Management System")

page = st.sidebar.radio("Navigation", ["Stream Views", "Manage Database","Chatbot"])

# ------------------ PAGE 1: STREAM TABLES ------------------
if page == "Stream Views":

    st.subheader("📊 Employee Allocation by Stream")

    streams_df = get_streams(conn)

    for _, row in streams_df.iterrows():
        st.markdown(f"### 🌐 {row['stream_name']}")

        matrix = get_stream_allocation(conn, row["stream_id"])

        if matrix.empty:
            st.info("No data available")
        else:
            st.dataframe(matrix, use_container_width=True)

        st.divider()


# ------------------ PAGE 2: MANAGE DATABASE ------------------
elif page == "Manage Database":

    st.subheader("⚙️ Manage Database")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Add Employee",
        "Add Role",
        "Add Shift",
        "Assign Employee"
    ])

    # ---- Add Employee ----
    with tab1:
        name = st.text_input("Name")
        email = st.text_input("Email")
        dept = st.text_input("Department")
        join = st.date_input("Joining Date")

        if st.button("Add Employee"):
            add_employee(conn, name, email, dept, str(join))
            st.success("Employee added!")

    # ---- Add Role ----
    with tab2:
        role = st.text_input("Role Name")
        desc = st.text_area("Description")

        if st.button("Add Role"):
            add_role(conn, role, desc)
            st.success("Role added!")

    # ---- Add Shift ----
    with tab3:
        shift = st.text_input("Shift Name")
        start = st.time_input("Start Time")
        end = st.time_input("End Time")

        if st.button("Add Shift"):
            add_shift(conn, shift, str(start), str(end))
            st.success("Shift added!")

    # ---- Add Allocation ----
    with tab4:
        emp_df = get_table(conn, "Employee")
        role_df = get_table(conn, "Role")
        shift_df = get_table(conn, "Shift")
        stream_df = get_table(conn, "Stream")

        emp = st.selectbox(
            "Employee",
            emp_df["employee_id"],
            format_func=lambda x: emp_df.loc[emp_df["employee_id"] == x, "name"].values[0]
        )

        role = st.selectbox(
            "Role",
            role_df["role_id"],
            format_func=lambda x: role_df.loc[role_df["role_id"] == x, "role_name"].values[0]
        )

        shift = st.selectbox(
            "Shift",
            shift_df["shift_id"],
            format_func=lambda x: shift_df.loc[shift_df["shift_id"] == x, "shift_name"].values[0]
        )

        stream = st.selectbox(
            "Stream",
            stream_df["stream_id"],
            format_func=lambda x: stream_df.loc[stream_df["stream_id"] == x, "stream_name"].values[0]
        )

        start = st.date_input("Start Date")

        if st.button("Assign"):
            add_allocation(conn, emp, role, shift, stream, str(start))
            st.success("Allocation added!")

# ------------------ PAGE 3: CHATBOT ------------------
else:
    chatbot()