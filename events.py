# TODO: Add option to supply events.csv location; if none is given, default to the repo CSV. Probably involves figuring out how
#  to handle command line arguments in batch files.
# TODO: Address the comment in main() from 2018 lol.

"""Alert the user at startup to upcoming events from the supplied text files."""
import configparser
import csv
from calendar import setfirstweekday, monthcalendar
from datetime import datetime


class CurrentYear:
    """Create and populate an object holding the events that occur in the current year."""
    mothers_day = "05-"
    fathers_day = "06-"
    month = 5    # Mother's Day is always in May, the fifth month
    sundays = 2  # Mother's Day is always the second Sunday in May

    def __init__(self):
        self.now = datetime.now()
        self.today = self.now.strftime("%m-%d-%Y")
        self.this_year_str = self.now.strftime("%Y")
        self.this_year_int = int(self.this_year_str)

    def get_last_varying_values(self, config):
        """
        Get the values for Mother's Day, Father's Day, and the year of the script's last run as listed in varying_values.ini. If this
        is the first run of the year (or some other reason the values don't align with this_year) they will be updated first.

        :return: List of the last run's values for Mother's Day, Father's Day, and the year run.
        """
        varying_values = ["last_year_ran", "last_fathers_day", "last_mothers_day"]
        config.read("varying_values.ini")
        if config.get("last_known_values", varying_values[0]) is not self.this_year_str:
            # Gets the dates for this year's Mother's and Father's Days
            # 6-11-18: Logic error where new dates would never be fetched may occur if file year is correct but the dates aren't
            # Given this should only happen if dates were manually changed, it was deemed too unlikely to occur to bother fixing
            self.set_new_varying_values(config)
        for i, var in enumerate(varying_values):
            varying_values[i] = config.get("last_known_values", var)
        return [varying_values[0], varying_values[1], varying_values[2]]

    def set_new_varying_values(self, config):
        """Set new values for Mother's Day, Father's Day, and the year ran."""
        self.mothers_day += self.get_day()
        self.month += 1    # Father's Day is always in June, the sixth month
        self.sundays += 1  # Father's Day is always the third Sunday in June
        self.fathers_day += self.get_day()
        with open("varying_values.ini", "w") as conf:
            config["last_known_values"]["last_mothers_day"] = self.mothers_day
            config["last_known_values"]["last_fathers_day"] = self.fathers_day
            config["last_known_values"]["last_year_ran"] = self.this_year_str
            config.write(conf)

    def get_day(self):
        """
        Get the month and day (MM-DD) of the specified holiday.

        :return: A string of the date.
        """
        i = 0
        setfirstweekday(6)
        for week in monthcalendar(self.this_year_int, self.month):
            if week[0] == 0:  # Sunday being the last day of the week by default
                continue  # If the first day of the month is not Sunday, disregard that week
            else:
                i += 1
                if i == self.sundays:
                    return str(week[0])

    def get_events(self):
        """
        Get events listed in events.csv

        :return: Items of the gathered event dictionary.
        """
        events = {self.fathers_day + "-" + self.this_year_str: "Father's Day",
                  self.mothers_day + "-" + self.this_year_str: "Mother's Day"}
        with open("events.csv", "r") as csvfile:
            dict_list = list(csv.DictReader(csvfile))
        self.list_values(dict_list, events, False)
        if self.now.strftime("%m") == "12":
            self.list_values(dict_list, events, True)
        return events.items()

    def list_values(self, dict_list, events, december):
        """
        Abstract out the dictionary-list conversion and add the values present in the CSV to the events dictionary.

        :param dict_list: List of dictionaries from the CSV reader.
        :param events: Event dictionary to store events from CSV.
        :param december: Boolean determining if the current month is December, necessary to add next January's events if needed.
        :return: The filled events dictionary.
        """
        for dictionary in dict_list:
            list_values = list(dictionary.values())
            if not december:
                for i, event in enumerate(list_values):
                    if i == 0:
                        events[list_values[i] + "-" + self.this_year_str] = list_values[i+1].rstrip("\n")
            else:
                for i, event in enumerate(list_values):
                    if i == 0 and event.startswith("01-"):
                        events[list_values[i] + "-" + str(self.this_year_int+1)] = list_values[i+1].rstrip("\n")
                    else:
                        break
        return events


class EventReminder:
    """Create and populate an object holding the event lists for each timeframe."""
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
        t = datetime.strptime(self.current_year.today, "%m-%d-%Y")
        for date, event in self.current_year.event_items:
            d = datetime.strptime(date, "%m-%d-%Y")
            if 0 < (d - t).days <= 1:  # Alternatively, use "date == self.current_year.today:"
                self.this_day.append((date, event))
            elif 1 < (d - t).days <= 7:
                self.this_week.append((date, event))
            elif 7 < (d - t).days <= 31:
                self.this_month.append((date, event))
        return [self.this_month, self.this_week, self.this_day]

    def print_events(self):
        """Print events occurring in the next month, week, and day."""
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
                print("\nIf you haven't picked up a gift yet, you might want to now!\n")
            if self.this_day:
                print("~*~*~*~*~\n\nThe following events are occurring today:\n")
                for event in self.this_day:
                    print("     >{0} : {1}".format(*event))
                print("\nCall them sometime today!")


def main():
    """Instantiate the CurrentYear and EventReminder objects, and print upcoming events."""
    current_year = CurrentYear()
    config = configparser.ConfigParser()
    current_year.get_last_varying_values(config)
    current_year.event_items = current_year.get_events()

    event_reminder = EventReminder(current_year)
    event_reminder.print_events()


# Initialize main function
if __name__ == "__main__":
    main()
