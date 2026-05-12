import sqlite3
import pandas as pd

def get_connection():
    return sqlite3.connect("KGP_OPS.db", check_same_thread=False)

# ---- Get all streams ----
def get_streams(conn):
    return pd.read_sql("SELECT * FROM Stream", conn)

# ---- Get allocation for a specific stream ----
def get_stream_allocation(conn, stream_id):
    query = f"""
    SELECT 
        e.name,
        r.role_name,
        s.shift_name,
        st.stream_name
    FROM Employee e
    JOIN EmployeeAllocation ea ON e.employee_id = ea.employee_id
    JOIN Role r ON ea.role_id = r.role_id
    JOIN Shift s ON ea.shift_id = s.shift_id
    JOIN Stream st ON ea.stream_id = st.stream_id
    WHERE ea.end_date IS NULL AND st.stream_id = {stream_id}
    """

    df = pd.read_sql(query, conn)

    if df.empty:
        return pd.DataFrame()

    # Pivot (Role vs Shift)
    matrix = df.pivot_table(
        index="role_name",
        columns="shift_name",
        values="name",
        aggfunc=lambda x: ", ".join(x)
    )

    return matrix.fillna("-")


# ---- Dropdown data ----
def get_table(conn, table):
    return pd.read_sql(f"SELECT * FROM {table}", conn)


# ---- Insert functions ----
def add_employee(conn, name, email, dept, join_date):
    conn.execute(
        "INSERT INTO Employee (name, email, department, joining_date) VALUES (?, ?, ?, ?)",
        (name, email, dept, join_date)
    )
    conn.commit()

def add_role(conn, role, desc):
    conn.execute(
        "INSERT INTO Role (role_name, description) VALUES (?, ?)",
        (role, desc)
    )
    conn.commit()

def add_shift(conn, name, start, end):
    conn.execute(
        "INSERT INTO Shift (shift_name, start_time, end_time) VALUES (?, ?, ?)",
        (name, start, end)
    )
    conn.commit()

def add_allocation(conn, emp, role, shift, stream, start_date):
    conn.execute(
        """INSERT INTO EmployeeAllocation 
        (employee_id, role_id, shift_id, stream_id, start_date)
        VALUES (?, ?, ?, ?, ?)""",
        (emp, role, shift, stream, start_date)
    )
    conn.commit()