
import os
import logging
import mysql.connector

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)

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

    # Enable SSL certificate verification
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

    logger.info("Home API called")

    return {
        "message": "My Second Project API is running"
    }


# POST API - Insert user
@app.post("/users", status_code=201)
def create_user(user: User):

    conn = None
    cursor = None

    try:

        logger.info("POST /users called for email: %s", user.email)

        # Connect to database
        conn = get_db_connection()

        logger.info("Database connection established")

        cursor = conn.cursor()

        # Insert query
        query = """
            INSERT INTO users (name, email)
            VALUES (%s, %s)
        """

        cursor.execute(query, (user.name, user.email))

        conn.commit()

        user_id = cursor.lastrowid

        logger.info(
            "User inserted successfully. User ID: %s",
            user_id
        )

        return {
            "message": "User created successfully",
            "user_id": user_id,
            "name": user.name,
            "email": user.email
        }

    except mysql.connector.Error:

        logger.exception("POST /users database operation failed")

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

            logger.info("Database connection closed")


# GET API - Retrieve all users
@app.get("/users")
def get_users():

    conn = None
    cursor = None

    try:

        logger.info("GET /users called")

        # Connect to database
        conn = get_db_connection()

        logger.info("Database connection established")

        cursor = conn.cursor(dictionary=True)

        # Retrieve query
        query = """
            SELECT id, name, email
            FROM users
            ORDER BY id DESC
        """

        cursor.execute(query)

        users = cursor.fetchall()

        logger.info(
            "Retrieved %s user records successfully",
            len(users)
        )

        return {
            "total": len(users),
            "users": users
        }

    except mysql.connector.Error:

        logger.exception("GET /users database operation failed")

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve users"
        )

    finally:

        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()

            logger.info("Database connection closed")
