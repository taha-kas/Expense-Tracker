from db.database import create_user

"""
    This script is used to seed the database with test users. 
    It creates a few sample users with predefined credentials for testing purposes.
    Feel free to modify the user data as needed for your testing scenarios.
"""

def seed_users():
    print("Seeding test users...\n")

    users = [
        ("john_doe", "john@example.com", "John123!", "1998-05-12"),
        ("alice_smith", "alice@example.com", "Alice456!", "2000-09-23"),
        ("bob_wilson", "bob@example.com", "Bob789!", "1995-01-30"),
    ]

    for username, email, password, birthday in users:
        user = create_user(username, email, password, birthday)
        if user:
            print(f"Created user: {username}")
        print("-" * 40)

if __name__ == "__main__":
    seed_users()