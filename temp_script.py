import datetime

# Read the contents of the log file
log_file_path = 'c:/data/contents.log'
dates_file_path = 'c:/data/contents.dates'

# Initialize a counter for Sundays
sunday_count = 0

with open(log_file_path, 'r') as log_file:
    # Read each line in the log file
    for line in log_file:
        # Try to parse each line as a date
        try:
            # Assuming each line contains a date in the format YYYY-MM-DD
            date = datetime.datetime.strptime(line.strip(), '%Y-%m-%d')
            # Check if the date is a Sunday
            if date.weekday() == 6:  # 6 corresponds to Sunday
                sunday_count += 1
        except ValueError:
            # Handle the case where line is not a valid date
            continue

# Write the count of Sundays to the output file
date_output = f'Number of Sundays: {sunday_count}'
with open(dates_file_path, 'w') as dates_file:
    dates_file.write(date_output)
