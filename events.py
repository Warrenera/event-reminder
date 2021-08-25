"""Alert the user to upcoming events from the supplied text files."""
import argparse
import configparser
import csv
import os
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

    def get_last_varying_values(self):
        """
        Get the values for Mother's Day and Father's Day as listed in varying_values.ini. If this is the first run of the year (or if
        there is some other reason the values don't align with this_year) they will be updated first.
        """
        config = configparser.ConfigParser()
        config.read("varying_values.ini")
        if config.get("last_known_values", "last_year_ran") != self.this_year_str:
            new_values = [self.this_year_str, self.get_day(self.mothers_day)]
            self.month, self.sundays = (1 + x for x in (self.month, self.sundays))
            new_values.append(self.get_day(self.fathers_day))

            with open("varying_values.ini", "w") as conf:
                for i, option in enumerate(config.options("last_known_values")):
                    config["last_known_values"][option] = new_values[i]
                config.write(conf)
        self.mothers_day = config.get("last_known_values", "last_mothers_day")
        self.fathers_day = config.get("last_known_values", "last_fathers_day")

    def get_day(self, month_of_day):
        """
        Get the month and day (MM-DD) of the specified holiday.

        :return: A string of the date.
        """
        i = 0
        setfirstweekday(6)  # Sets Sunday as the first day of the week
        for week in monthcalendar(self.this_year_int, self.month):
            if week[0] == 0:  # Sunday being the last day of the week by default
                continue  # If the first day of the month is not Sunday, disregard that week
            else:
                i += 1
                if i == self.sundays:
                    return month_of_day + str(week[0])

    def get_events(self, filepath):
        """
        Get events listed in events.csv.

        :param filepath: Filepath of events.csv if different from default.
        :return: Items of the gathered event dictionary.
        """
        events = {self.fathers_day + "-" + self.this_year_str: "Father's Day",
                  self.mothers_day + "-" + self.this_year_str: "Mother's Day"}

        with open(filepath if filepath else "events.csv", "r") as csvfile:
            list_of_dicts = list(csv.DictReader(csvfile))
        december = True if self.now.strftime("%m") == "12" else False
        return self.list_values(list_of_dicts, events, december)

    def list_values(self, list_of_dicts, events, december):
        """
        Abstract out the dictionary-list conversion and add the values present in the CSV to the events dictionary.

        :param list_of_dicts: List of dictionaries from the CSV reader.
        :param events: Event dictionary to store events from CSV.
        :param december: Boolean determining if the current month is December, necessary to add next January's events if needed.
        :return: The filled events dictionary.
        """
        for dictionary in list_of_dicts:
            list_values = list(dictionary.values())
            # list_values[0] will always be a date, list_values[1] an event
            if december and list_values[0].startswith("01-"):
                events[list_values[0] + "-" + str(self.this_year_int+1)] = list_values[1].rstrip("\n")
            else:
                events[list_values[0] + "-" + self.this_year_str] = list_values[1].rstrip("\n")
        return events.items()


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

        :return: Finalized lists of events occurring in the next 30 days, 7 days, and 1 day, respectively.
        """
        t = datetime.strptime(self.current_year.today, "%m-%d-%Y")
        for date, event in self.current_year.event_items:
            d = datetime.strptime(date, "%m-%d-%Y")
            if 0 < (d - t).days <= 1:
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


def main(filepath):
    """Instantiate the CurrentYear and EventReminder objects, and print upcoming events."""
    current_year = CurrentYear()
    current_year.get_last_varying_values()
    current_year.event_items = current_year.get_events(filepath)

    event_reminder = EventReminder(current_year)
    event_reminder.print_events()


def parse_arguments():
    """Parse an optional command line argument pointing to the location of events.csv"""
    parser = argparse.ArgumentParser(description="Location of events.csv")
    parser.add_argument("-fp", "--filepath", type=str, help="The location of events.csv")

    args = parser.parse_args()
    if args.filepath:
        if not os.path.exists(args.filepath):
            raise argparse.ArgumentTypeError("Invalid filepath")
    return args.filepath


# Initialize main function
if __name__ == "__main__":
    main(parse_arguments())
