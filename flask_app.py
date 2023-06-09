from dotenv import load_dotenv

load_dotenv()
from urllib.request import urlopen
from datetime import datetime
import flask
from os import getenv
import logging
from telebot.types import Update
from main import bot, FILE_URL


formatter = "[%(asctime)s] %(levelname)8s --- %(message)s (%(filename)s:%(lineno)s)"
logging.basicConfig(
    filename=f"flask-{datetime.now().date()}.log",
    filemode="w",
    format=formatter,
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)

app = flask.Flask(__name__)

logging.error("TEST")

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
    logging.info(FILE_URL.format(file_path="/photos/" + slug))
    file = urlopen(FILE_URL.format(file_path="/photos/" + slug))
    return flask.send_file(file, download_name="image.jpg")


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)
    app.run(debug=getenv("DEBUG"))
