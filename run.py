from app import create_app, db

app = create_app()  

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode

