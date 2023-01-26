import requests
import datetime as dt
import pandas as pd
import calendar
import pytz
import robot_api

# API Key that allows us to make GET/POST/DELETE requests to the robots (to make/delete visitor passes)
# Stored in another file to keep out robots anonymous (i.e., I don't want to post it on github)
api_key = robot_api.api_key

# Link we want to send users to after the call
afterURL = ""

# Dictionary that maps robot's nickname to the key to be used for API calls
# Stored in another file to keep out robots anonymous (i.e., I don't want to post it on github)
# It's a dictionary with the key: value format of SerialNumber: RobotKey, where robot key is the format r_##### and can be found on DoubleRobotics Fleet Management
robot_dictionary = robot_api.robot_dictionary

# A given driver will have passes generated using the following information:
#       name - The name of the driver (for reference)
#       robot_name - The nickname for the robot they will call into
#       email - the email to send the visitor pass to
#       duration - length of call in minutes
#       day - the day of the week we want to schedule recurring meetings for
#       time_hr - the hour that the call will start (24Hr time)
#       time_min - how many minutes past the start of the hour that the call will start at
#       e.g., for time_hr and time_min: time_hr = 13 and time_min = 30 will start a call at 13:30 or 1:30PM
class Robot_Driver:
    def __init__(self, name, robot_name, robot_serial, email, duration, day, time_hr, time_min):
        self.name = name
        self.robot_name = robot_name
        self.robot_serial = robot_serial
        self.email = email
        self.duration = duration
        self.day = day
        self.time_hr = time_hr
        self.time_min = time_min

# Initialize different users that will need recurring meetings
# Create array of all drivers
drivers = []

# Main, controls whole script
def main():
    # Call to load user data from spreadsheet
    drivers = load_data()

    # Get weekday
    # Legend: 0 - Monday, 1 - Tuesday, ..., 6 - Sunday
    today = dt.datetime.today().weekday()

    # Loop through all drivers, send pass if the driver's booking is on this day
    for i in range(len(drivers)):
        if (drivers[i].day == today):
            request_pass(drivers[i])


# Load user data from spreadsheet
# Takes data from spreadsheet 
def load_data():
    df = pd.read_excel(robot_api.path_to_spreadsheet, sheet_name = "Bookings")

    # Drop all rows that are incomplete 
    df.dropna()

    # TODO - Output error message/notify charlie to indicate if file is messed up!
    # NOT IMPLEMENTED

    # Loop through all our drivers stored in the list (one per row), setup our variables
    for i in range(len(df)):
        # append i'th driver into our list of drivers
        # Convert datetime to string
        [time_hr, time_min] = parse_time(df.Start_Time[i])
        day_formatted = map_day(df.Day[i])
        x = Robot_Driver(name = df.Name[i], robot_name = df.Robot_Name[i], robot_serial = df.Robot_Serial[i], email = df.Email[i], time_hr = time_hr, time_min = time_min, day = day_formatted, duration = df.Duration[i])
        drivers.append(x)
    return drivers

# Takes in date, formats it into proper UTC datetime form for request
def format(time_hr, time_min):
    date = dt.datetime.today()
    #date = dt.datetime.today() + dt.timedelta(days=1)
    formatted_date_local = date.replace(hour=time_hr, minute = time_min, second= 0, microsecond= 0)
    formatted_date_UTC = formatted_date_local.astimezone(pytz.utc)
    str_date = formatted_date_UTC.strftime("%Y-%m-%d %H:%M:%S")
    return str_date

# Takes in start time of format HH:MM and returns hours and minutes separately, both as integers
# Also takes in day and maps it to
def parse_time(start_time):
    string_time = start_time.strftime("%H:%M")
    time_hr, time_min = string_time.split(":")
    return int(time_hr), int(time_min)

# Take in day as string, map it to integer value
def map_day(day):
    days = dict(zip(calendar.day_name, range(7))); 
    day_formatted = days[day]
    return int(day_formatted)

# Function to test sending a post request
def request_pass(user):
    # Extract user data
    robot_name = user.robot_name
    robot_serial = user.robot_serial
    email = user.email
    duration = user.duration
    time = user.duration
    start_hr = user.time_hr
    start_min = user.time_min
    day = user.day

    # Find key given robot name
    robot_key = str(robot_dictionary[str(robot_serial)])

    # Format date properly
    date_formatted = format(start_hr, start_min)

    # Create POST request for a given user
    # Parameters for POST
    request_url = str("https://admin.doublerobotics.com/api/v1/robots/" + robot_key + "/visitor-passes")
    authentication_header = {"Authorization": api_key, 'Content-Type': 'application/x-www-form-urlencoded'}
    payload = "start=" + date_formatted + "&duration=" + str(duration) + "&email=" + email + "&fromUsername=clake13"
    
    # Send request, check whether request was successful
    request_return = requests.post(request_url, data = payload, headers = authentication_header)
    #request_return = requests.post("https://admin.doublerobotics.com/api/v1/robots/", headers = authentication_header)

# run on load
if __name__ == '__main__':
    main()