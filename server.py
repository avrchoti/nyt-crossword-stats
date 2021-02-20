import colorsys
import base64
import os
import re

import numpy

import history
import plot
import webresources
from flask import Flask, render_template, request, url_for

import logging
import status
from dfreader import read_df

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
def dstatus():
    df = read_df()
    status_values = status.calc_status(df)
    graph_uri = url_for("graphs", solved="1")
    recent_history = history.calc_history(df)
    recent_history = render_history(recent_history)
    return render_template("status.html", graph_uri=graph_uri, status=status_values, recent_history=recent_history)


def render_history(history):
    res = {}
    for ts, values in history.items():
        day = ts.strftime("%Y-%m-%d")
        print(day)
        week = {}
        for weekday, factor in values.items():
            x = {"val": "%0.2f" % factor, "color": pick_color(factor)}
            week[weekday] = x
        res[day] = week
    return res


def pick_color(factor):
    """
       0.5 ... green
       1 .... white
       2 .... red

       linear gradient between 0.5 and 1 and 1 and 2
    """
    SATURATION_FACTOR = 2  # linear between 1 and this
    if factor < 1:
        x = 1 / factor
    else:
        x = factor

    if x >= SATURATION_FACTOR:
        x = SATURATION_FACTOR

    if factor > 1:
        hue = 0
    else:
        hue = 0.33
    x = x - 1  ## range 0 .. 1
    # x = 1 - x ### range 1 .. 0
    #- x = x * 255
    rgb = colorsys.hsv_to_rgb(hue, x, 1.0)
    print(rgb)
    return "#" + "".join(["%02x" % int(x*255) for x in rgb])


@app.route("/graphs")
def graphs():
    df = read_df()
    filters = []
    solved = request.args.get("solved", None)
    if solved is not None:
        filters.append(f"solved={solved}")
        df = df[df.solved == int(solved)]

    df = filter_time(df, request.args, filters)

    imagedata = plot.timetrend(df, ",".join(filters))
    imagedata = base64.b64encode(imagedata).decode("utf-8")

    histdata = plot.box_per_day(df, ",".join(filters))
    histdata = base64.b64encode(histdata).decode("utf-8")

    plotxx = plot.plot2xx(df, ",".join(filters))
    plotxx = base64.b64encode(plotxx).decode("utf-8")

    return render_template("graphs.html", imagedata=imagedata, histdata=histdata, plotxx=plotxx)


def filter_time(df, args, filters):
    start = parse_day(args.get("start"))
    x = ["["]
    if start is not None:
        df = df[df.date > start]
        x.append(args.get("start"))

    x.append(":")
    end = parse_day(args.get("end"))
    if end is not None:
        df = df[df.date < end]
        x.append(args.get("end"))

    x.append("]")
    filters.append("".join(x))
    return df


def parse_day(day):
    if day is None:
        return None
    rex = re.compile("now-([0-9]+)d")
    match = rex.match(day)
    if match:
        days = int(match.group(1))
        return numpy.datetime64("today") - numpy.timedelta64(days, "D")

    res = numpy.datetime64(day)
    return res


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
