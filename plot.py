import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot(df, filters):
    pivoted = df.pivot(index="date", columns="day", values="elapsed_seconds")
    pivoted = pivoted.interpolate()

    WINSIZE = 140

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

    ax.set_title( f"Time trend, averaged over {WINSIZE} - {filters}")
    output = io.BytesIO()
    plt.savefig(output, format="png")
    output.seek(0)
    return output.getbuffer()
