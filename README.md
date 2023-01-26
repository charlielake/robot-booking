# double3-robot-booking
Script to parse a given .xlsx file and automate sending telerobot passes to users on a regular basis (once a week, at a given time).

* Booking_spreadsheet_example.xlsx is an example spreadsheet that explains the formatting of values. 
* booking_system.py is the main script that runs to send out passes. It uses the Mac Process Automator to run once a day at midnight.
* robot_api.py is referenced in the script booking_system.py. This is simply a file that stores some confidential variables we want to avoid sharing (it has patient information!). But the structure of the variables are explained in the booking_system.py script.