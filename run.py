from app import create_app, db
from app.models.admin import Admin
from werkzeug.security import generate_password_hash  

app = create_app()  

# Custom CLI command to create an admin user
@app.cli.command()
def create_admin():
    """Create an admin user."""
    from getpass import getpass

    username = input('Enter admin username: ')
    password = getpass('Enter admin password: ')

    # Hash the password
    password_hash = generate_password_hash(password)

    # Create the admin user
    admin = Admin(username=username, password_hash=password_hash)
    db.session.add(admin)
    db.session.commit()

    print('Admin user created successfully.')


if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode

