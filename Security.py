import os
import json

# Path to the user-pass JSON file
user_pass_file = 'File/data/user_pass.json'

# Ensure the directory exists
os.makedirs(os.path.dirname(user_pass_file), exist_ok=True)

# Initialize an empty dictionary to hold user-pass data
users_pass = {"users": []}

# Check if the user_pass_file exists
if os.path.exists(user_pass_file):
    try:
        # Load existing user data from JSON file
        with open(user_pass_file, 'r') as pass_file:
            users_pass = json.load(pass_file)
    except json.JSONDecodeError:
        # Handle JSON decode error by initializing with a default structure
        users_pass = {"users": []}


# Function to check if the JSON file is empty or does not exist
def is_user_pass_empty():
    if os.path.exists(user_pass_file):
        # Check if the file size is greater than 0
        if os.path.getsize(user_pass_file) > 0:
            with open(user_pass_file, 'r') as file:
                data = json.load(file)
                # Check if 'users' key exists and is an empty list
                return 'users' in data and len(data['users']) == 0
        else:
            return True
    else:
        return True


# Function to add a user
def add_user(user_id, username, password):
    # Check if the user already exists
    for user in users_pass["users"]:
        if user["Id"] == user_id:
            return 'Signup Error: User Already Exists!'

    # Create a new user entry
    new_user = {
        "Id": user_id,
        "user": username,
        "password": password
    }
    # Append the new user to the list of users
    users_pass["users"].append(new_user)

    # Save the updated user-pass data back to the JSON file
    with open(user_pass_file, 'w') as file:
        json.dump(users_pass, file, indent=4)

    return 'Signup Completed!'


# Function to edit a user
def edit_user(user_id, new_username=None, new_password=None):
    # Iterate over the list of users to find the user with the matching ID
    for user in users_pass["users"]:
        # print(user['Id'])
        if user["Id"] == user_id:
            # Update the username and/or password if new values are provided
            if new_username:
                user["user"] = new_username
            if new_password:
                user["password"] = new_password

            # Save the updated user-pass data back to the JSON file
            with open(user_pass_file, 'w') as file:
                json.dump(users_pass, file, indent=4)
            return f'{new_username} update successful!'
    # Return False if the user is not found
    return f'{new_username} Not Found!'


# Function to delete a user
def delete_user(user_id):
    # Iterate over the list of users to find the user with the matching ID
    for i, user in enumerate(users_pass["users"]):
        if user["Id"] == user_id:
            # Remove the user from the list
            del users_pass["users"][i]

            # Save the updated user-pass data back to the JSON file
            with open(user_pass_file, 'w') as file:
                json.dump(users_pass, file, indent=4)
            return f'{user_id} deleted successful!'
    # Return False if the user is not found
    return f'{user_id} Not Found!'


# Function to check the password of a user
def check_password(user_id, password):
    # Iterate over the list of users to find the user with the matching ID
    for user in users_pass["users"]:
        if user["Id"] == user_id:
            # Check if the provided password matches the stored password
            return user["password"] == password
    # Return False if the user is not found or the password does not match
    return False



