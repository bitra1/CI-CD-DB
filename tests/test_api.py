
import os
import uuid

import mysql.connector
from fastapi.testclient import TestClient

from common import app, get_db_connection

client = TestClient(app)


# Prepare the temporary test database
def setup_test_database():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(150)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def test_post_and_get_user():

    setup_test_database()

    unique_email = f"{uuid.uuid4().hex}@example.com"

    # POST API - Insert record
    post_response = client.post(
        "/users",
        json={
            "name": "Murthy",
            "email": unique_email
        }
    )

    assert post_response.status_code == 201

    inserted_user = post_response.json()

    assert inserted_user["name"] == "Murthy"
    assert inserted_user["email"] == unique_email

    # GET API - Retrieve records
    get_response = client.get("/users")

    assert get_response.status_code == 200

    result = get_response.json()

    assert result["total"] >= 1

    matching_users = [
        user for user in result["users"]
        if user["email"] == unique_email
    ]

    assert len(matching_users) == 1
    assert matching_users[0]["name"] == "Murthy"
