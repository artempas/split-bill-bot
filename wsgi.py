from flask_app import app, WEBHOOK_HOST
from dotenv import load_dotenv
from os import getenv

if __name__ == '__main__':
    load_dotenv()
    app.run(app.run(debug=getenv("DEBUG")))