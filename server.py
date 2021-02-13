import base64
import os

import pandas

import plot
import webresources
from flask import Flask, render_template, url_for, request, redirect, make_response, flash

import logging
import files

template_folder = webresources.web_resources_root() / "templates"
static_folder = webresources.web_resources_root() / "static"

app = Flask(__name__, template_folder=str(template_folder), static_folder=str(static_folder))
app.config.from_object(__name__)
app.config['SECRET_KEY'] = "7651103ebada48dab3599ff702d7c85d"

from flask.logging import default_handler

app.logger.removeHandler(default_handler)
app.logger.disabled = True
wz_logger = logging.getLogger('werkzeug')
wz_logger.disabled = True

logger = logging.getLogger()
logger.level = logging.INFO


@app.route("/")
def index():
    df = pandas.read_csv(files.data_file(), parse_dates=["date"])

    imagedata = plot.plot(df)
    with open( "xoxo.png", "wb") as of:
        of.write( imagedata )
    imagedata= base64.b64encode(imagedata).decode("utf-8")
    return render_template("index.html", imagedata=imagedata)


def runapp(app, host, port, debug):
    logger.info(
        "Starting server. WERKZEUG_RUN_MAIN=%s, debug=%s" % (
            os.environ.get("WERKZEUG_RUN_MAIN"), debug))
    if not debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # Put here initializations that need to happen once
        pass
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    PORT = 5099

    runapp(app, host="0.0.0.0", port=PORT, debug=True)
