import sqlite3
import random
from datetime import datetime, timedelta

# =========================================================
# DATABASE CONNECTION
# =========================================================

conn = sqlite3.connect("KGP_OPS.db")

# IMPORTANT: Enable foreign key constraints in SQLite
conn.execute("PRAGMA foreign_keys = ON")

cursor = conn.cursor()

# =========================================================
# DROP EXISTING TABLES (OPTIONAL FOR CLEAN REBUILD)
# =========================================================

cursor.execute("DROP TABLE IF EXISTS EmployeeAllocation")
cursor.execute("DROP TABLE IF EXISTS Employee")
cursor.execute("DROP TABLE IF EXISTS Role")
cursor.execute("DROP TABLE IF EXISTS Shift")
cursor.execute("DROP TABLE IF EXISTS Stream")

# =========================================================
# CREATE TABLES
# =========================================================

# ---------------- EMPLOYEE ----------------

cursor.execute("""
CREATE TABLE Employee (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    department TEXT,
    joining_date TEXT
)
""")

# ---------------- ROLE ----------------

cursor.execute("""
CREATE TABLE Role (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT NOT NULL,
    description TEXT
)
""")

# ---------------- SHIFT ----------------

cursor.execute("""
CREATE TABLE Shift (
    shift_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shift_name TEXT NOT NULL,
    start_time TEXT,
    end_time TEXT
)
""")

# ---------------- STREAM ----------------

cursor.execute("""
CREATE TABLE Stream (
    stream_id INTEGER PRIMARY KEY AUTOINCREMENT,
    stream_name TEXT NOT NULL,
    description TEXT
)
""")

# ---------------- EMPLOYEE ALLOCATION ----------------

cursor.execute("""
CREATE TABLE EmployeeAllocation (

    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,

    employee_id INTEGER,
    role_id INTEGER,
    shift_id INTEGER,
    stream_id INTEGER,

    start_date TEXT,
    end_date TEXT,

    FOREIGN KEY (employee_id)
        REFERENCES Employee(employee_id)
        ON DELETE CASCADE,

    FOREIGN KEY (role_id)
        REFERENCES Role(role_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (shift_id)
        REFERENCES Shift(shift_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (stream_id)
        REFERENCES Stream(stream_id)
        ON DELETE RESTRICT
)
""")

# =========================================================
# DATA GENERATION
# =========================================================

# ---------------- EMPLOYEES ----------------

names = [
    "Amit",
    "Neha",
    "Rahul",
    "Priya",
    "Karan",
    "Sneha",
    "Vikram",
    "Rohit",
    "Anjali",
    "Pooja"
]

departments = [
    "IT",
    "HR",
    "Finance",
    "Operations"
]

employees = []

for i in range(1, 121):

    name = random.choice(names) + f"_{i}"

    email = name.lower() + "@company.com"

    dept = random.choice(departments)

    join_date = datetime.now() - timedelta(
        days=random.randint(100, 1500)
    )

    employees.append((
        name,
        email,
        dept,
        join_date.strftime("%Y-%m-%d")
    ))

cursor.executemany("""
INSERT INTO Employee
(name, email, department, joining_date)
VALUES (?, ?, ?, ?)
""", employees)

# =========================================================
# ROLES
# =========================================================

roles = [
    (
        f"Role_{i}",
        f"Description for role {i}"
    )
    for i in range(1, 21)
]

cursor.executemany("""
INSERT INTO Role
(role_name, description)
VALUES (?, ?)
""", roles)

# =========================================================
# SHIFTS
# =========================================================

shifts = [
    ("Morning", "08:00", "16:00"),
    ("General", "09:00", "17:00"),
    ("Late Morning", "10:00", "18:00"),
    ("Afternoon", "12:00", "20:00"),
    ("Evening", "14:00", "22:00"),
    ("Night", "20:00", "04:00"),
    ("Flexible", "11:00", "19:00"),
    ("Split", "06:00", "10:00")
]

cursor.executemany("""
INSERT INTO Shift
(shift_name, start_time, end_time)
VALUES (?, ?, ?)
""", shifts)

# =========================================================
# STREAMS
# =========================================================

streams = [
    ("Support", "Customer support"),
    ("Development", "Software development"),
    ("Analytics", "Data analytics"),
    ("Compliance", "Regulatory work"),
    ("Testing", "QA and testing")
]

cursor.executemany("""
INSERT INTO Stream
(stream_name, description)
VALUES (?, ?)
""", streams)

# =========================================================
# EMPLOYEE ALLOCATION
# =========================================================

employee_ids = list(range(1, 121))
role_ids = list(range(1, 21))
shift_ids = list(range(1, 9))
stream_ids = list(range(1, 6))

allocations = []

for emp in employee_ids:

    role = random.choice(role_ids)

    shift = random.choice(shift_ids)

    stream = random.choice(stream_ids)

    start_date = datetime.now() - timedelta(
        days=random.randint(30, 500)
    )

    allocations.append((
        emp,
        role,
        shift,
        stream,
        start_date.strftime("%Y-%m-%d"),
        None
    ))

cursor.executemany("""
INSERT INTO EmployeeAllocation
(
    employee_id,
    role_id,
    shift_id,
    stream_id,
    start_date,
    end_date
)
VALUES (?, ?, ?, ?, ?, ?)
""", allocations)

# =========================================================
# COMMIT & CLOSE
# =========================================================

conn.commit()

conn.close()

print("✅ Clean normalized database created successfully!")