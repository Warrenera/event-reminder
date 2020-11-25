# TODO: Look into using actual data structure like JSON instead of custom "x : y" text formatting
# TODO: Look into official commenting etiquette for good comment hygiene

from calendar import setfirstweekday, monthcalendar
from datetime import datetime


def get_current_list():
    """
    Read events from text file; gets last known year, Mother's, and Father's day

    :return: dict of important events
    :return: last known year the program was run
    :return: Mother's Day this year
    :return: Father's Day this year
    """
    events = {}
    with open("events.txt", "r") as file:
        for line in file:
            if line.startswith("0") or line.startswith("1"):
                (key, val) = line.split(" : ")
                events[key] = val.rstrip("\n")
            elif line.startswith("y"):
                last_year_ran = int(line[4:])
            elif line.startswith("f"):
                last_fathers_day = line[4:].rstrip("\n")
            elif line.startswith("m"):
                last_mothers_day = line[4:].rstrip("\n")
    return events.items(), last_year_ran, last_fathers_day, last_mothers_day


def get_varying_days(event_items, last_mothers_day, last_fathers_day, current_year):
    next_mothers_day = "05-"
    next_fathers_day = "06-"
    month = 5    # Mother's Day is always in May, the fifth month
    sundays = 2  # Mother's Day is always the second Sunday in May

    for i in range(0, 2):
        if i == 0:
            next_mothers_day += get_day(current_year, month, sundays)
        else:
            month += 1    # Father's Day is always in June, the sixth month
            sundays += 1  # Father's Day is always the third Sunday in June
            next_fathers_day += get_day(current_year, month, sundays)

    with open("events.txt", "w") as file:
        file.write("m : " + next_mothers_day + "\n")
        file.write("f : " + next_fathers_day + "\n")
        file.write("y : " + str(current_year) + "\n")
        for date, event in event_items:
            if date == last_mothers_day:
                date = next_mothers_day
            elif date == last_fathers_day:
                date = next_fathers_day
            file.write(date + " : " + event + "\n")


def get_day(current_year, month, sundays):
    i = 0
    setfirstweekday(6)  # Sets the first day of the week to Sunday
    for week in monthcalendar(current_year, month):
        if week[0] == 0:
            continue  # If the first day of the month is not Sunday, disregard that week
        else:
            i += 1
            if i == sundays:
                return str(week[0])


def append_events(event_items, today, this_month, this_week, this_day):
    for date, event in event_items:
        d = datetime.strptime(date, "%m-%d")
        t = datetime.strptime(today, "%m-%d")

        if 0 <= (d - t).days <= 31:
            this_month.append((date, event))
        if 0 <= (d - t).days <= 7:
            this_week.append((date, event))
        if date == today:
            this_day.append((date, event))
    return [this_month, this_week, this_day]


def print_events(this_month, this_week, this_day):
    print("Hello! Welcome to your family and friend birthday and important event reminder, brought to you by wonderful Python!")

    if not this_month and not this_week and not this_day:
        print("It looks like there aren't any events coming up!")
    else:
        if this_month:
            print("Just a heads up, the following events are occurring in the next thirty days:\n")
            for event in this_month:
                print("     >{0} : {1}".format(*event))
            print("\nI recommend you start looking for a gift!\n")

        if this_week:
            print("~*~*~*~*~\n\nThe following events are occurring in the next seven days:\n")
            for event in this_week:
                print("     >{0} : {1}".format(*event))
            print("\nIf you haven't picked up a gift yet, you need to now!\n")

        if this_day:
            print("~*~*~*~*~\n\nThe following events are occurring today:\n")
            for event in this_day:
                print("     >{0} : {1}".format(*event))
            print("\nCall them sometime today!")


def main():
    this_month = []
    this_week = []
    this_day = []

    now = datetime.now()
    today = now.strftime("%m-%d")
    current_year = int(now.strftime("%Y"))

    event_items, last_year_ran, last_fathers_day, last_mothers_day = get_current_list()

    # Gets the dates for this year's Mother's and Father's Days
    # 6-11-18: Logic error where new dates would never be fetched may occur if file year is correct but the dates aren't
    # Given this should only happen if dates were manually changed, it was deemed too unlikely to occur to bother fixing
    if last_year_ran != current_year:
        get_varying_days(event_items, last_mothers_day, last_fathers_day, current_year)

    this_month, this_week, this_day = append_events(event_items, today, this_month, this_week, this_day)

    print_events(this_month, this_week, this_day)


# Initializes main function
if __name__ == "__main__":
    main()


# Hello there