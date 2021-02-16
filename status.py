import numpy
import pandas
import files


def calc_status(df, today=None):
    if today is None:
        today = numpy.datetime64("today")

    res = {}
    calc_today_status(df, today, res)
    calc_streak_status(df, today, res)

    return res


def calc_today_status(df, today, res):
    last = df[df.date == today]
    # print( last )
    today_status = "missing"
    secs_today = None
    if len(last.index) == 1:
        row = last.iloc[0]
        if row.streak_eligible:
            today_status = "streak"
            secs_today = row.elapsed_seconds
        elif row.solved:
            today_status = "done"
            secs_today = row.elapsed_seconds
        else:
            today_status = "open"
    res["today_done"] = today_status
    if secs_today is not None:
        res["secs_today"] = secs_today


def calc_streak_status(df, today, res):
    finder = StreakFinder()
    streaks = finder.find_streaks(df)
    res["streaks"] = streaks

class StreakFinder:
    def __init__(self):
        self.start_date = None
        self.streak_len = 0
        self.streaks = []

    def find_streaks(self, df):
        # find streaks
        for index, row in df.iterrows():
            if row.streak_eligible:
                if self.start_date is None:
                    self.start_date = row.date
                    self.streak_len = 1
                else:
                    self.streak_len += 1
                self.end_date = row.date

            else:
                if self.start_date is not None:
                    self.finish_streak()

        if self.start_date is not None:
            self.finish_streak()

        return self.streaks

    def finish_streak(self):
        print(f"streak from {self.start_date} to {self.end_date} - {self.streak_len} days")
        streak = {"days": self.streak_len, "start_date": self.start_date, "end_date": self.end_date}
        self.streaks.append(streak)
        self.start_date = None
        self.streak_len = 0
