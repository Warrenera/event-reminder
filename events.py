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
    month = 5  # Mother's Day is always in May, the fifth month
    sundays = 2  # Mother's Day is always the second Sunday in May

    def __init__(self, filepaths):
        self.filepaths = filepaths
        self.now = datetime.now()
        self.today = self.now.strftime("%m-%d-%Y")
        self.this_month_str = self.now.strftime("%m")
        self.this_year_str = self.now.strftime("%Y")
        self.this_year_int = int(self.this_year_str)

    def set_varying_values(self):
        """
        Get the values for Mother's Day and Father's Day as listed in varying_values.ini. If this is the first run of the year (or if
        there is some other reason the values don't align with this_year) they will be updated first.
        """

        def _get_day(month_of_day):
            """
            Get the month and day (MM-DD) of the specified holiday.

            :return: A string of the date.
            """
            j = 0
            setfirstweekday(6)  # Sets Sunday as the first day of the week
            for week in monthcalendar(self.this_year_int, self.month):
                if week[0] == 0:  # Sunday being the last day of the week by default
                    continue  # If the first day of the month is not Sunday, disregard that week
                else:
                    j += 1
                    if j == self.sundays:
                        return month_of_day + str(week[0])

        config = configparser.ConfigParser()
        config.read(self.filepaths["varying_values.ini"])
        if config.get("last_known_values", "last_year_ran") != self.this_year_str:
            new_values = [self.this_year_str, _get_day(self.mothers_day)]
            self.month, self.sundays = (1 + date for date in (self.month, self.sundays))
            new_values.append(_get_day(self.fathers_day))

            with open(self.filepaths["varying_values.ini"], "w") as conf:
                for i, option in enumerate(config.options("last_known_values")):
                    config["last_known_values"][option] = new_values[i]
                config.write(conf)
        self.mothers_day = config.get("last_known_values", "last_mothers_day")
        self.fathers_day = config.get("last_known_values", "last_fathers_day")

    def get_events(self):
        """
        Get events listed in events.csv.

        :return: Items of the gathered event dictionary.
        """
        events = {self.fathers_day + "-" + self.this_year_str: "Father's Day",
                  self.mothers_day + "-" + self.this_year_str: "Mother's Day"}

        with open(self.filepaths["events.csv"], "r") as csvfile:
            list_of_dicts = list(csv.DictReader(csvfile))
        december = True if self.this_month_str == "12" else False
        return self.list_values(list_of_dicts, events, december)

    def list_values(self, list_of_dicts, events, december):
        """
        Abstract out the dictionary-list conversion and add the values present in the CSV to the event dictionary.

        :param list_of_dicts: List of dictionaries from the CSV reader.
        :param events: Event dictionary to store events from CSV.
        :param december: Boolean determining if the current month is December, necessary to add next January's events if needed.
        :return: The filled event dictionary.
        """
        for dictionary in list_of_dicts:
            if len(dictionary) > 2:
                raise ValueError("Dictionary must only consist of a date and event.\n"
                                 "Expected: {'date': 'MM-DD', 'event': \"Event Description\"}\n"
                                 f"Got: {dictionary}")
            list_values = list(dictionary.values())
            if december and list_values[0].startswith("01-"):
                events[list_values[0] + "-" + str(self.this_year_int + 1)] = list_values[1].rstrip("\n")
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
            try:
                d = datetime.strptime(date, "%m-%d-%Y")
            except ValueError as e:
                print(f"ERROR: {repr(e)} occurred. Dictionary must consist of an MM-DD date, then a description of that date's event.")
            else:
                days_to_event = (d - t).days
                if 0 <= days_to_event < 1:
                    self.this_day.append((date, event))
                elif 1 <= days_to_event < 7:
                    self.this_week.append((date, event))
                elif 7 <= days_to_event < 31:
                    self.this_month.append((date, event))
        return [self.this_month, self.this_week, self.this_day]

    def print_events(self):
        """Print events occurring in the next month, week, and day."""
        print("Hello! Welcome to your family and friend birthday and important event reminder, brought to you by wonderful Python!")
        if not self.this_month and not self.this_week and not self.this_day:
            print("It looks like there aren't any events coming up!")
        else:
            if self.this_month:
                print("~*~*~*~*~\n\nJust a heads up, the following events are occurring in the next month:\n")
                for event in self.this_month:
                    print(f"     >{' : '.join(event)}")
                print("\nI recommend you start looking for a gift!\n")
            if self.this_week:
                print("~*~*~*~*~\n\nThe following events are occurring in the next week:\n")
                for event in self.this_week:
                    print(f"     >{' : '.join(event)}")
                print("\nIf you haven't picked up a gift yet, you might want to now!\n")
            if self.this_day:
                print("~*~*~*~*~\n\nThe following events are occurring today:\n")
                for event in self.this_day:
                    print(f"     >{' : '.join(event)}")
                print("\nCall them sometime today!\n")


def main(filepaths):
    """Instantiate the CurrentYear and EventReminder objects, and print upcoming events."""
    current_year = CurrentYear(filepaths)
    current_year.set_varying_values()
    current_year.event_items = current_year.get_events()

    event_reminder = EventReminder(current_year)
    event_reminder.print_events()


def parse_arguments():
    """Parse optional command line arguments pointing to the location of events.csv and varying_values.ini"""
    parser = argparse.ArgumentParser(description="Location of events.csv")
    parser.add_argument("-e", "--events", type=str, help="The location of events.csv", dest="events.csv")
    parser.add_argument("-v", "--varying_values", type=str, help="The location of varying_values.ini", dest="varying_values.ini")

    args = vars(parser.parse_args())
    for arg, filepath in args.items():
        try:
            os.path.isfile(filepath)
        except TypeError as e:
            print(f"INFO: Using default {arg} because {repr(e)} occurred.")
            default = {arg: arg}
            args.update(default)
    return args


# Initialize main function
if __name__ == "__main__":
    main(parse_arguments())
