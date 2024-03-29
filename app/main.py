import bcrypt
from typing import Union
from fastapi import FastAPI
from app.models import User
from db.supabase import create_supabase_client

app = FastAPI()

supabase = create_supabase_client()


def user_exists(key: str = "email", value: str = None):
    user = supabase.from_("users").select("*").eq(key, value).execute()
    return len(user.data) > 0


# Create a new user
@app.post("/user")
def create_user(user: User):
    try:
        # Convert email to all lowercase
        user_email = user.email.lower()
        # Hash the password
        hashed_password = bcrypt.hashpw(str.encode(user.password), bcrypt.gensalt())

        # does the user already exist?
        if user_exists(value=user_email):
            return {"message": "User already exists"}

        # Add new user to the database table
        user = supabase.from_("users") \
            .insert({"name": user.name, "email": user.email, "password": hashed_password}) \
            .execute()

        # Check to see if the user was in fact added
        if user:
            return {"message": "User created successfully"}
        else:
            return {"message": "User creation failed"}
    except Exception as e:
        print("Error: ", e)
        return {"message": "User Creation failed"}


# Get a user
@app.get("/user")
def get_user(user_id: Union[str, None] = None):
    try:
        if user_id:
            user = supabase.from_("users") \
                .select("id", "name", "email") \
                .eq("id", user_id) \
                .execute()

            if user:
                return user
        else:
            users = supabase.from_("users") \
                .select("id", "name", "email") \
                .execute()
            if users:
                return users
    except Exception as e:
        print(f"Error: {e}")
        return {"message": "User not found"}


# Update a user
@app.put("/user")
def update_user(user_id: str, email: str, name: str):
    try:
        user_email = email.lower()

        # Check if user exists
        if user_exists("id", user_id):
            # Check if email already exists
            email_exists = supabase.from_("users") \
                .select("*").eq("email", user_email) \
                .execute()
            if len(email_exists.data) > 0:
                return {"message": "Email already exists"}

            # Update user
            user = supabase.from_("users") \
                .update({"name": name, "email": user_email}) \
                .eq("id", user_id).execute()
            if user:
                return {"message": "User updated successfully"}
        else:
            return {"message": "User update failed"}
    except Exception as e:
        print(f"Error: {e}")
        return {"message": "User update failed"}


# Delete a user
@app.delete("/user")
def delete_user(user_id: str):
    try:
        # Check if user exists
        if user_exists("id", user_id):
            # Delete user
            supabase.from_("users") \
                .delete().eq("id", user_id) \
                .execute()
            return {"message": "User deleted successfully"}

        else:
            return {"message": "User deletion failed"}
    except Exception as e:
        print(f"Error: {e}")
        return {"message": "User deletion failed"}


@app.get("/")
def home_route():
    return {"message": "CodeNamor 2024 FastAPI Python CRUD API with SupaBase integration"}
