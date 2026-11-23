import os
import mysql.connector

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="My Second Project")


# Database connection
def get_db_connection():

    config = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", "4000")),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }

    # Enable certificate verification when CA is configured.
    ca_path = os.getenv("DB_SSL_CA")

    if ca_path:
        config.update({
            "ssl_ca": ca_path,
            "ssl_verify_cert": True,
            "ssl_verify_identity": True
        })

    return mysql.connector.connect(**config)


# Request model
class User(BaseModel):
    name: str
    email: str


# Home API
@app.get("/")
def home():
    return {"message": "My Second Project API is running"}


# POST API - Insert user
@app.post("/users", status_code=201)
def create_user(user: User):

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO users (name, email)
            VALUES (%s, %s)
        """

        cursor.execute(query, (user.name, user.email))
        conn.commit()

        return {
            "message": "User created successfully",
            "user_id": cursor.lastrowid,
            "name": user.name,
            "email": user.email
        }

    except mysql.connector.Error:
        if conn and conn.is_connected():
            conn.rollback()

        raise HTTPException(
            status_code=500,
            detail="Database operation failed"
        )

    finally:
        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


# GET API - Retrieve all users
@app.get("/users")
def get_users():

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, name, email
            FROM users
            ORDER BY id DESC
        """)

        users = cursor.fetchall()

        return {
            "total": len(users),
            "users": users
        }

    except mysql.connector.Error:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve users"
        )

    finally:
        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()
