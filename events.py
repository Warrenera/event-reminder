# TODO: Convert code from functional code to object-oriented code
# TODO: Look into using actual data structure like JSON instead of custom "x : y" text formatting
# TODO: Look into official commenting etiquette for good comment hygiene
# TODO: Look into ways to remove some magic numbers, lots of assumptions made in here
# TODO: Do I need a main()?

from calendar import setfirstweekday, monthcalendar, calendar
from datetime import datetime


def get_varying_days(event_items, this_year_m, this_year_f, current_year):
    next_m = "05-"
    next_f = "06-"
    month = 5    # Mother's Day is always in May, the fifth month
    sundays = 2  # Mother's Day is always the second Sunday in May

    for i in range(0, 2):
        if i == 0:
            next_m += get_day(current_year, month, sundays)
        else:
            month += 1    # Father's Day is always in June, the sixth month
            sundays += 1  # Father's Day is always the third Sunday in June
            next_f += get_day(current_year, month, sundays)

    with open("events.txt", "w") as file:
        file.write("m : " + next_m + "\n")
        file.write("f : " + next_f + "\n")
        file.write("y : " + str(current_year) + "\n")
        for date, event in event_items:
            if date == this_year_m:
                date = next_m
            if date == this_year_f:
                date = next_f
            file.write(date + " : " + event + "\n")


def get_day(current_year, month, sundays):
    i = 0
    setfirstweekday(calendar.SUNDAY)
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

    dt = datetime.now()
    today = dt.strftime("%m-%d")

    current_year = int(dt.strftime("%Y"))
    year = 0

    this_year_m = ""
    this_year_f = ""

    #  Reads events from text file; gets last known year, Mother's, and Father's day
    events = {}
    with open("events.txt", "r") as file:
        for line in file:
            if line.startswith("0") or line.startswith("1"):
                (key, val) = line.split(" : ")
                events[key] = val.rstrip("\n")
            elif line.startswith("y"):
                year = int(line[4:])
            elif line.startswith("f"):
                this_year_f = line[4:].rstrip("\n")
            elif line.startswith("m"):
                this_year_m = line[4:].rstrip("\n")

    event_items = events.items()

    # Gets the dates for this year's Mother's and Father's Days
    # 6-11-18: Logic error where new dates would never be fetched may occur if file year is correct but the dates aren't
    # Given this should only happen if dates were manually changed, it was deemed too unlikely to occur to bother fixing
    if year != current_year:
        get_varying_days(event_items, this_year_m, this_year_f, current_year)

    this_month, this_week, this_day = append_events(event_items, today, this_month, this_week, this_day)

    print_events(this_month, this_week, this_day)


#  Initializes main function
if __name__ == "__main__":
    main()
