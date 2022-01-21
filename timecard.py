#!/bin/python3

###########################################################################################
# Stephen-Hamilton-C
# Freely available to anyone who wishes to use this :D
# Place this script anywhere, and modify .bashrc so it runs this script with the auto arg.
# e.g. `python ~/timecard/timecard.py auto`
###########################################################################################

import sys, os, json, time
from datetime import date, datetime

# Setup constants
TIMECARD_FILE: str = './timecard.' + str(date.today()) + '.json'
EXPECTED_WORK_HOURS: int = 8 * 60 * 60
IS_INSTALLED = False # TODO: Determine if this script is already installed.
CAN_INSTALL = not IS_INSTALLED and False # TODO: This may not be necessary if there's no sudo perms required for what I have in mind 
# Ensure cwd is file dir
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# Cleanup old timecards, if any
for timeFile in os.listdir():
	if os.path.isfile(timeFile) and timeFile.startswith('timecard.') and timeFile.endswith('.json') and os.stat(timeFile).st_mtime < time.time() - 7*60*60*24:
		print('Removing old timecard: '+timeFile)
		os.remove(timeFile)

timeEntries: list = [ ]

def readFile():
	global timeEntries
	with open(TIMECARD_FILE, 'r') as timecardFile:
		timecardData: str = timecardFile.read()
		timeEntries = json.loads(timecardData)

def saveFile():
	with open(TIMECARD_FILE, 'w') as timecardFile:
		timeEntriesJson: str = json.dumps(timeEntries)
		timecardFile.write(timeEntriesJson)
  
def clockIn():
    newEntry: dict[str, int] = { "startTime": round(time.time()), "endTime": 0 }
    timeEntries.append(newEntry)
    
def clockOut():
    lastEntry: dict[str, int] = timeEntries[len(timeEntries) - 1]
    lastEntry['endTime'] = round(time.time())
    
def getClockState() -> str:
    # Clock state needs data to be loaded	
	if len(timeEntries) == 0:
		readFile()
	if timeEntries[len(timeEntries) - 1]['endTime'] == 0:
		return 'OUT'
	return 'IN'

def getTotalTimeWorked() -> int:
	timeSum: int = 0
	for timeEntry in timeEntries:
		if timeEntry['endTime'] == 0:
			# Use current time if this entry isn't finished yet
			timeSum += round(time.time()) - timeEntry['startTime']
		else:
			timeSum += timeEntry['endTime'] - timeEntry['startTime']
	return timeSum

def getTotalBreakTime() -> int:
	timeSum: int = 0
	for i in range(len(timeEntries)):
		timeEntry = timeEntries[i]
		if timeEntry['endTime'] == 0:
			continue
		if i+1 < len(timeEntries):
			timeSum += timeEntries[i+1]['endTime'] - timeEntry['startTime']
		else:
			timeSum += round(time.time()) - timeEntry['endTime']
	return timeSum

def getFormatter(timestamp: int) -> str:
	if timestamp < 60*60:
		# If the total time isn't even an hour, don't bother showing it
		return '%M min'
	return '%H hrs, %M min'

def remainingTimeCommand():
	# Calculate remaining time and expected end time
	totalWorked = getTotalTimeWorked()
	workRemaining = EXPECTED_WORK_HOURS - totalWorked
	endTime = round(time.time()) + workRemaining
	localized = datetime.fromtimestamp(endTime)

	formattedRemaining = time.strftime(getFormatter(workRemaining), time.gmtime(workRemaining))
	formattedLocalized = localized.strftime('%H:%M')

	print(formattedRemaining + ' left:')
	print(formattedLocalized)

    
def clockCommand():
	clockState = getClockState()
	print('Clocking ' + clockState.lower() + '...')
	if clockState == 'IN':
		clockIn()
		remainingTimeCommand()
	elif clockState == 'OUT':
		clockOut()
		hoursWorkedCommand()
	saveFile()
 
def hoursWorkedCommand():
	timeSum: int = getTotalTimeWorked()

	# Calculate the nearest quarter hour to input into a timesheet database
	totalTime = time.gmtime(timeSum)
	nearestQuarterHour = totalTime.tm_hour + ((round(totalTime.tm_min/15) * 15) % 60) / 60

	# Format the time
	formattedTime = time.strftime(getFormatter(timeSum), totalTime)

	# Report to the user the results
	print('Started work at '+datetime.fromtimestamp(timeEntries[0]['startTime']).strftime('%H:%M'))
	# TODO: Print off entire log of entries for the day
	print()
	print('Total time worked:')
	print(formattedTime)
	print(str(nearestQuarterHour) + ' hours')
	print()
	print('Time remaining to get ' + str(int(EXPECTED_WORK_HOURS/60/60)) + ' hours:')
	remainingTimeCommand()
	print()
	print('Total time on break:')
	totalBreakTimeCommand()

def totalBreakTimeCommand():
	# FIXME: Test this some more... after clocking in, it's 10 minutes off
	timeSum: int = getTotalBreakTime()
	totalTime = time.gmtime(timeSum)

	formattedTime = time.strftime(getFormatter(timeSum), totalTime)

	print(formattedTime)


def installCommand():
	if CAN_INSTALL:
		print('Automatic installing is not yet supported. Sorry!')
		# TODO: Implement installing script into system
	else:
		print('Unable to install at this time. Is timecard.py already installed?')

def uninstallCommand():
	print('Automatic installing is not yet supported, so there\'s no way I can uninstall this!')
	# TODO: Implement uninstalling once installing is implemented

def getArgument() -> str:
	if len(sys.argv) > 1:
		return sys.argv[1].strip().upper()
	return None

if getArgument() == 'INSTALL':
	print('Install script')
elif not os.path.exists(TIMECARD_FILE):
    # Timecard doesn't exist for today yet, prompt user
	prompt = input('Clock in for the day? (Y/n): ').strip().lower()

	# Set prompt to first char, if there are any
	if len(prompt) > 0:
		prompt = prompt[0]

	# Default answer is YES
	# Also make sure the user hasn't done this in another instance
	if prompt != 'n' and not os.path.exists(TIMECARD_FILE):
		clockIn()
		saveFile()
		
elif getArgument() == 'AUTO':
    # Script was run automatically by .bashrc (if configured that way) and timecard already exists
	print('Timecard already present for today. If you need to clock ' + getClockState().lower() + ', run `python '+__file__+'`')
else:
	readFile()
  
	# Determine if we are clocking in or out
	clockState = getClockState()
	
	# Try to get command from argument
	action = getArgument()
	if action == None:
		# Argument doesn't exist, get command from user
		# TODO: Remove WORKED, REMAINING, and BREAK to replace with STATUS or something. Report all data at once.
		# TODO: Remove input and only take input via command. Show usage if arg is not recognized
		commands = clockState + '|WORKED|REMAINING|BREAK'
		if CAN_INSTALL:
			commands += '|INSTALL'
		if IS_INSTALLED:
			commands += '|UNINSTALL'
		action = input('Possible commands: (' + commands + '): ').strip().upper()
		
	if action == clockState or (len(action) > 0 and action[0] == clockState[0]):
		clockCommand()
	elif action == 'WORKED' or (len(action) > 0 and action[0] == 'W'):
		hoursWorkedCommand()
	elif action == 'BREAK' or (len(action) > 0 and action[0] == 'B'):
		totalBreakTimeCommand()
	elif action == 'REMAINING' or (len(action) > 0 and action[0] == 'R'):
		remainingTimeCommand()
	elif action == 'INSTALL' or (len(action) > 0 and action[0] == 'I'):
		installCommand()
	elif action == 'UNINSTALL' or (len(action) > 0 and action[0] == 'U'):
		uninstallCommand()
	else:
		print('Unknown command.')