import pprint

from numpy import datetime64, timedelta64

from days import DAYS_MON_FIRST


def calc_history(df):
    today = datetime64("today")
    cutoff = today - timedelta64(365, "D")
    last_year = df[df.date <= today][df.date > cutoff]
    # print( last_year)

    pivoted = last_year.pivot(index="date", columns="day", values="elapsed_seconds")
    # pivoted = pivoted.interpolate()
    medians = {}
    for day in DAYS_MON_FIRST:
        median = pivoted[day].median()
        medians[day] = median
        pivoted[f"MED_{day}"] = median
    # print(medians)
    print(pivoted)

    res = {}
    week = {}
    monday = None
    for index, row in last_year.iterrows():
        day = row["day"]
        if day == "Mon":
            monday = row["date"]
        val = row["elapsed_seconds"] / medians[day]
        week[day] = val
        if day == "Sun":
            if monday is not None:
                res[monday] = week
            week = {}
    if monday is not None:
        res[monday] = week

    pprint.pprint(res)
    return res