from fastapi import FastAPI
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# -----------------------------------
# DATABASE CONNECTION
# -----------------------------------
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
        ssl_disabled=False,
        auth_plugin="mysql_native_password"
    )

# -----------------------------------
# CREATE TABLE ON STARTUP
# -----------------------------------
@app.on_event("startup")
def create_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            expense_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            amount FLOAT,
            category VARCHAR(100),
            description TEXT,
            payment_method VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        cursor.close()
        conn.close()

        print("✅ Table checked/created successfully")

    except Exception as e:
        print("❌ Table creation error:", e)

# -----------------------------------
# HOME
# -----------------------------------
@app.get("/")
def home():
    return {"message": "Backend is running"}

# -----------------------------------
# TEST DB
# -----------------------------------
@app.get("/test-db")
def test_db():
    try:
        conn = get_db_connection()
        conn.close()
        return {"message": "Database Connected"}
    except Exception as e:
        return {"error": str(e)}

# -----------------------------------
# ADD EXPENSE
# -----------------------------------
@app.post("/expenses")
def add_expense(expense: dict):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO expenses (title, amount, category, description, payment_method, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        """

        values = (
            expense.get("title"),
            expense.get("amount"),
            expense.get("category"),
            expense.get("description", ""),
            expense.get("payment_method", "Cash")
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        return {"message": "Expense Added Successfully"}

    except Exception as e:
        return {"error": str(e)}

# -----------------------------------
# GET ALL EXPENSES
# -----------------------------------
@app.get("/expenses")
def get_expenses():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM expenses ORDER BY expense_id DESC")
        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return {"expenses": data}

    except Exception as e:
        return {"error": str(e)}

# -----------------------------------
# UPDATE EXPENSE
# -----------------------------------
@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: dict):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        UPDATE expenses
        SET title=%s, amount=%s, category=%s, description=%s, payment_method=%s
        WHERE expense_id=%s
        """

        values = (
            expense.get("title"),
            expense.get("amount"),
            expense.get("category"),
            expense.get("description", ""),
            expense.get("payment_method", "Cash"),
            expense_id
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        return {"message": "Expense Updated Successfully"}

    except Exception as e:
        return {"error": str(e)}

# -----------------------------------
# DELETE EXPENSE
# -----------------------------------
@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM expenses WHERE expense_id=%s", (expense_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return {"message": "Expense Deleted Successfully"}

    except Exception as e:
        return {"error": str(e)}

# -----------------------------------
# SEARCH EXPENSE
# -----------------------------------
@app.get("/search")
def search_expense(category: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM expenses WHERE category=%s", (category,))
        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return {"expenses": data}

    except Exception as e:
        return {"error": str(e)}

# -----------------------------------
# SORT EXPENSES
# -----------------------------------
@app.get("/sort")
def sort_expenses(sort_by: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if sort_by == "price_desc":
            query = "SELECT * FROM expenses ORDER BY amount DESC"
        elif sort_by == "price_asc":
            query = "SELECT * FROM expenses ORDER BY amount ASC"
        elif sort_by == "date_asc":
            query = "SELECT * FROM expenses ORDER BY expense_id ASC"
        else:
            query = "SELECT * FROM expenses ORDER BY expense_id DESC"

        cursor.execute(query)
        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return {"expenses": data}

    except Exception as e:
        return {"error": str(e)}