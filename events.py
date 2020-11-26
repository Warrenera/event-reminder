"""Alert the user at startup to upcoming events from the supplied text files."""
import csv
import configparser
from datetime import datetime
from calendar import setfirstweekday, monthcalendar


class CurrentYear:
    """Create and populate an object holding the events that occur in the current year."""
    mothers_day = "05-"
    fathers_day = "06-"
    month = 5    # Mother's Day is always in May, the fifth month
    sundays = 2  # Mother's Day is always the second Sunday in May

    def __init__(self):
        self.now = datetime.now()
        self.today = self.now.strftime("%m-%d")
        self.this_year = int(self.now.strftime("%Y"))

        self.config = configparser.ConfigParser()
        self.last_year_ran, self.last_fathers_day, self.last_mothers_day = self.get_last_varying_values(self.config)
        self.event_items = self.get_events()

    def get_last_varying_values(self, config):
        """
        Get the values for M<other's Day, Father's Day, and the year of the script's last run.

        :param config: A ConfigParser instance to read the values from varying_values.ini.
        :return: The last run's values for Mother's Day, Father's Day, and the year run.
        """
        varying_values = ["last_year_ran", "last_fathers_day", "last_mothers_day"]
        config.read("varying_values.ini")
        for i, var in enumerate(varying_values):
            varying_values[i] = self.config.get("last_known_values", var)
        return [varying_values[0], varying_values[1], varying_values[2]]

    def get_events(self):
        """
        Get events listed in events.csv

        :return: Items of the gathered event list.
        """
        events = {self.last_fathers_day: "Father's Day", self.last_mothers_day: "Mother's Day"}
        with open("events.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                events[row["date"]] = row["event"].rstrip("\n")
        return events.items()

    def set_new_varying_values(self):
        """Set new values for Mother's Day, Father's Day, and the year ran."""
        for i in range(0, 2):
            if i == 0:
                self.mothers_day += self.get_day()
            else:
                self.month += 1    # Father's Day is always in June, the sixth month
                self.sundays += 1  # Father's Day is always the third Sunday in June
                self.fathers_day += self.get_day()
        with open("varying_values.ini", "w") as conf:
            self.config["last_known_values"]["last_mothers_day"] = self.mothers_day
            self.config["last_known_values"]["last_fathers_day"] = self.fathers_day
            self.config["last_known_values"]["last_year_ran"] = str(self.this_year)
            self.config.write(conf)

    def get_day(self):
        """
        Get the day and month (MM-DD) of the specified holiday.

        :return: A string of the date.
        """
        i = 0
        setfirstweekday(6)  # Sets the first day of the week to Sunday
        for week in monthcalendar(self.this_year, self.month):
            if week[0] == 0:
                continue  # If the first day of the month is not Sunday, disregard that week
            else:
                i += 1
                if i == self.sundays:
                    return str(week[0])


class EventReminder:
    """
    Create and populate an object holding the event lists for each timeframe.
    """
    def __init__(self, current_year):
        self.current_year = current_year
        self.this_month = []
        self.this_week = []
        self.this_day = []
        self.this_month, self.this_week, self.this_day = self.append_events()

    def append_events(self):
        """
        Append the events gathered in the CurrentYear object to their respective lists.

        :return: Finalized lists of events occurring in the next 30 days, 7 days, and 1 day.
        """
        for date, event in self.current_year.event_items:
            d = datetime.strptime(date, "%m-%d")
            t = datetime.strptime(self.current_year.today, "%m-%d")

            if 7 < (d - t).days <= 31:
                self.this_month.append((date, event))
            if 1 < (d - t).days <= 7:
                self.this_week.append((date, event))
            if date == self.current_year.today:
                self.this_day.append((date, event))
        return [self.this_month, self.this_week, self.this_day]

    def print_events(self):
        """Print events occurring in the next month, week, and today."""
        print("Hello! Welcome to your family and friend birthday and important event reminder, brought to you by wonderful Python!")

        if not self.this_month and not self.this_week and not self.this_day:
            print("It looks like there aren't any events coming up!")
        else:
            if self.this_month:
                print("Just a heads up, the following events are occurring in the next month:\n")
                for event in self.this_month:
                    print("     >{0} : {1}".format(*event))
                print("\nI recommend you start looking for a gift!\n")
            if self.this_week:
                print("~*~*~*~*~\n\nThe following events are occurring in the next week:\n")
                for event in self.this_week:
                    print("     >{0} : {1}".format(*event))
                print("\nIf you haven't picked up a gift yet, you need to now!\n")
            if self.this_day:
                print("~*~*~*~*~\n\nThe following events are occurring today:\n")
                for event in self.this_day:
                    print("     >{0} : {1}".format(*event))
                print("\nCall them sometime today!")


def main():
    """Instantiate the CurrentYear and EventReminder objects, and print upcoming events."""
    current_year = CurrentYear()
    event_reminder = EventReminder(current_year)

    # Gets the dates for this year's Mother's and Father's Days
    # 6-11-18: Logic error where new dates would never be fetched may occur if file year is correct but the dates aren't
    # Given this should only happen if dates were manually changed, it was deemed too unlikely to occur to bother fixing
    if current_year.last_year_ran != current_year.this_year:
        current_year.set_new_varying_values()

    event_reminder.print_events()


# Initializes main function
if __name__ == "__main__":
    main()
