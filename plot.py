import datetime
import io
import matplotlib
import numpy

import seaborn as sns
from matplotlib.dates import HourLocator, DateFormatter

from status import calc_today_status

DAYS_MON_FIRST = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAYS_SUN_FIRST = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def timetrend(df, filters):
    pivoted = df.pivot(index="date", columns="day", values="elapsed_seconds")
    pivoted = pivoted.interpolate()

    WINSIZE = 28

    pivoted["Mon_AVG"] = pivoted["Mon"].rolling(window=WINSIZE).mean()
    pivoted["Tue_AVG"] = pivoted["Tue"].rolling(window=WINSIZE).mean()
    pivoted["Wed_AVG"] = pivoted["Wed"].rolling(window=WINSIZE).mean()
    pivoted["Thu_AVG"] = pivoted["Thu"].rolling(window=WINSIZE).mean()
    pivoted["Fri_AVG"] = pivoted["Fri"].rolling(window=WINSIZE).mean()
    pivoted["Sat_AVG"] = pivoted["Sat"].rolling(window=WINSIZE).mean()
    pivoted["Sun_AVG"] = pivoted["Sun"].rolling(window=WINSIZE).mean()

    # ax = plt.gca()
    fig, ax = plt.subplots()
    kind = "line"
    pivoted.plot(kind=kind, y="Mon_AVG", ax=ax)
    pivoted.plot(kind=kind, y="Tue_AVG", ax=ax)
    pivoted.plot(kind=kind, y="Wed_AVG", ax=ax)
    pivoted.plot(kind=kind, y="Thu_AVG", ax=ax)
    pivoted.plot(kind=kind, y="Fri_AVG", ax=ax)
    pivoted.plot(kind=kind, y="Sat_AVG", ax=ax)
    pivoted.plot(kind=kind, y="Sun_AVG", ax=ax)

    ax.set_title(f"Time trend, averaged over {WINSIZE} - {filters}")
    return savefig()


def savefig():
    output = io.BytesIO()
    plt.savefig(output, format="png")
    output.seek(0)
    return output.getbuffer()


def box_per_day(df, filters):
    fig, ax = plt.subplots()

    sns.boxplot(x="day", y="elapsed_seconds", order=DAYS_MON_FIRST, data=df)

    sns.stripplot(x="day", y="elapsed_seconds", order=DAYS_MON_FIRST, data=df, size=2, color=".3", linewidth=0)
    # sns.swarmplot(x="day", y="elapsed_seconds", order=DAYS, data=df, size=2, color=".3", linewidth=0)
    ax.xaxis.grid(True)
    ax.yaxis.grid(True)
    ax.set(ylabel="seconds")
    ax.set_title(f"Time distribution - {filters}")
    return savefig()


def plot2xxx(df, filters):
    fig, axes = plt.subplots(7, 1)

    for idx, day in enumerate(DAYS):
        filtered = df[df.day == day]
        # filtered = filtered["elapsed_seconds"]
        axes[idx].set_title(day)
        # filtered.plot.hist(by="elapsed_seconds", bins=20, ax=axes[idx])
        sns.histplot(x="elapsed_seconds", data=filtered, ax=axes[idx])
    return savefig()


def plot2xx(df, filters):
    fig, ax = plt.subplots()
    day = datetime.datetime.now().weekday()
    day = DAYS_MON_FIRST[day]
    print("weekday", day)




    filtered = df[df.day == day]
    sns.histplot(x="elapsed_seconds", data=filtered, ax=ax)
    # adding a vertical line for the average passengers per flight
    secs_today =get_time_today(filtered)
    if secs_today is not None:
        plt.axvline(secs_today, color="purple", label="hooga")
        plt.text(secs_today,  # x-coordinate position of data label, adjusted to be 3 right of the data point
                 y=max([h.get_height() for h in ax.patches]),  # y-coordinate position of data label, to take max height
                 s=f"today:{secs_today}", color="purple")  # colour of the vertical mean line
    ax.set_title(f"Distribution for {day}")
    return savefig()

def get_time_today( df, today = None):
    if today is None:
        today = numpy.datetime64("today")

    res = {}
    calc_today_status(df, today, res)
    return res.get("secs_today")