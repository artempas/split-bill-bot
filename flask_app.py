from dotenv import load_dotenv
import time
load_dotenv()
from urllib.request import urlopen
from datetime import datetime
import flask
from os import getenv
from telebot.types import Update
from main import bot, FILE_URL



app = flask.Flask(__name__)


WEBHOOK_HOST = getenv("host")

WEBHOOK_URL_BASE = "https://%s" % (WEBHOOK_HOST)
WEBHOOK_URL_PATH = "/%s/" % (getenv("TELETOKEN"))


# Empty webserver index, return nothing, just http 200
@app.route("/", methods=["GET", "HEAD"])
def index():
    return ""


@app.route(WEBHOOK_URL_PATH, methods=["POST"])
def webhook():
    if flask.request.headers.get("content-type") == "application/json":
        json_string = flask.request.get_data().decode("utf-8")
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return ""
    else:
        flask.abort(403)


@app.route("/photos/<slug>", methods=["GET"])
def forward_image(slug):
    print("Request from outside: "+FILE_URL.format(file_path="/photos/" + slug))
    file = urlopen(FILE_URL.format(file_path="/photos/" + slug))
    return flask.send_file(file, download_name="image.jpg")


if __name__ == "__main__":
    print(f"Binding webhook to {WEBHOOK_URL_BASE+WEBHOOK_URL_PATH}")
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)
    app.run(debug=getenv("DEBUG"))
