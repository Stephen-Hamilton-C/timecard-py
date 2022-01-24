#!/usr/bin/python3

###########################################################################################
# Stephen-Hamilton-C - Licensed under the GNU GPL v3 License.
# Source code can be found at https://github.com/Stephen-Hamilton-C/Timecard
# Place this script anywhere, and modify .bashrc so it runs this script with the auto arg.
# e.g. `python3 ~/timecard/timecard.py auto`
###########################################################################################

import sys, os, stat, json, time
from datetime import date, datetime
from platform import system
from shutil import move

# Setup constants
SCRIPT_PATH = os.path.realpath(__file__)
EXPECTED_WORK_HOURS: int = 8 * 60 * 60
TIMECARD_FILE: str = 'timecard.' + str(date.today()) + '.json'
TIMECARD_PATH: str = os.path.expanduser('~/.local/share/timecard')
INSTALL_DIR: str = os.path.expanduser('~/.local/bin')
if system() == 'Windows':
	TIMECARD_PATH = os.path.expanduser('~\\AppData\\Local\\timecard')
	INSTALL_DIR = os.path.expanduser('~')

# Ensure cwd is timecard dir
if not os.path.exists(TIMECARD_PATH):
	os.makedirs(TIMECARD_PATH)
os.chdir(TIMECARD_PATH)

# Cleanup old timecards, if any
for timeFile in os.listdir():
	if os.path.isfile(timeFile) and timeFile.startswith('timecard.') and timeFile.endswith('.json') and os.stat(timeFile).st_mtime < time.time() - 7*60*60*24:
		print('Removing old timecard: '+timeFile)
		os.remove(timeFile)

isInstalled = os.path.exists(os.path.join(INSTALL_DIR, 'timecard.py')) or os.path.exists(os.path.join(INSTALL_DIR, 'timecard'))
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

	print('Time remaining to get ' + str(int(EXPECTED_WORK_HOURS/60/60)) + ' hours:')
	print(formattedRemaining + ' left')
	print(formattedLocalized)
	print()

    
def clockCommand(clockState):
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
	print('Total time worked:')
	print(formattedTime)
	print(str(nearestQuarterHour) + ' hours')
	print()

def totalBreakTimeCommand():
	# FIXME: Test this some more... after clocking in, it's 10 minutes off
	# Before clocking back in, the break time is accurate. After clocking in, it's off by several minutes.
	timeSum: int = getTotalBreakTime()
	totalTime = time.gmtime(timeSum)

	formattedTime = time.strftime(getFormatter(timeSum), totalTime)

	print('Total time on break:')
	print(formattedTime)
	print()

def statusCommand():
	# TODO: Print off entire log of entries for the day
	print('Started work at '+datetime.fromtimestamp(timeEntries[0]['startTime']).strftime('%H:%M'))
	print()
	hoursWorkedCommand()
	remainingTimeCommand()
	totalBreakTimeCommand()

def aliasPrompt(bashrcPath, exePath):
	aliasPrompt = input('Do you want to add alias timecard="python3 '+exePath+'" to your .bashrc to get around this? (Y/n): ').strip().upper()
	if aliasPrompt != 'n':
		with open(bashrcPath, 'a') as bashrcFile:
			bashrcFile.write('alias timecard="python3 '+exePath+'" #timecard\n')

def installCommand():
	if isInstalled:
		print('timecard.py is already installed!')
	else:
		if not os.path.exists(INSTALL_DIR):
			os.makedirs(INSTALL_DIR)

		if system() == 'Windows':
			move(SCRIPT_PATH, os.path.join(INSTALL_DIR, 'timecard.py'))
			print('Installed to ' + INSTALL_DIR + '. Use `python3 timecard.py` to run the script')
		else:
			bashrcPath = os.path.expanduser('~/.bashrc')
			exePath = os.path.join(INSTALL_DIR, 'timecard')
			move(SCRIPT_PATH, exePath)
			with open(bashrcPath, 'a') as bashrcFile:
				bashrcFile.write('\n# Timecard autorun\n')
				bashrcFile.write('python3 ' + exePath + ' auto #timecard\n')
			try:
				os.chmod(exePath, stat.S_IRWXU)
				PATH = os.getenv('PATH')
				if PATH.find('.local/bin') == -1:
					pathPrompt = input('Do you want to add ~/.local/bin to your PATH? This will allow you to run timecard like a command. (Y/n): ').strip().upper()
					if pathPrompt != 'n':
						with open(bashrcPath, 'a') as bashrcFile:
							bashrcFile.write('PATH=$PATH:~/.local/bin #timecard\n')
					else:
						aliasPrompt(bashrcPath, exePath)
			except Exception:
				print('Unable to make timecard.py executable! You\'ll have to use `python3 timecard.py` to run Timecard.')
				aliasPrompt(bashrcPath, exePath)
			# TODO: Add prompt to see if user wants to add .local/bin to their path
			with open(bashrcPath, 'a') as bashrcFile:
				bashrcFile.write('\n')
			print('Installed to ' + INSTALL_DIR + '. Ensure that is in your PATH and then use `timecard` to run the script')


def uninstallCommand():
	if isInstalled:
		for timeFile in os.listdir():
			if timeFile.startswith('timecard.') and timeFile.endswith('.json'):
				os.remove(timeFile)
		if system() != 'Windows':
			os.chdir('..')
			os.rmdir('timecard')

			bashrcLines = []
			with open(os.path.expanduser('~/.bashrc'), 'r') as bashrcFile:
				bashrcLines = bashrcFile.readlines()
			with open(os.path.expanduser('~/.bashrc'), 'w') as bashrcFile:
				for line in bashrcLines:
					strippedLine = line.strip()
					if strippedLine != '# Timecard autorun' and not strippedLine.endswith('#timecard'):
						bashrcFile.write(line)
			# TODO: Add prompt to see if user wants to remove .local/bin from their PATH
		print('timecard.py has been uninstalled!')
		os.remove(SCRIPT_PATH)
	else:
		print('timecard.py is not installed!')

def getArgument() -> str:
	if len(sys.argv) > 1:
		return sys.argv[1].strip().upper()
	return ' '

def printUsage():
	print('Usage: timecard <INSTALL|UNINSTALL | CLOCK|IN|OUT>')





# Check for this first so that we aren't prompting the user about clocking in if all they want to do is install
if getArgument() == 'INSTALL' or getArgument()[0] == 'I':
	installCommand()
elif getArgument() == 'UNINSTALL' or getArgument()[0] == 'U':
	uninstallCommand()
elif not os.path.exists(TIMECARD_FILE):
    # Timecard doesn't exist for today yet, prompt user
	prompt = input('Clock in for the day? (Y/n): ').strip().lower()

	# Set prompt to first char, if there are any
	if len(prompt) > 0:
		prompt = prompt[0]

	# Default answer is YES
	# Also make sure the user hasn't done this in another instance
	if prompt != 'n' and not os.path.exists(TIMECARD_FILE):
		clockCommand('IN')
		
elif getArgument() == 'AUTO':
    # Script was run automatically by .bashrc (if configured that way) and timecard already exists
	print('Timecard already present for today. If you need to clock ' + getClockState().lower() + ', run `python3 '+__file__+'`')
else:
	readFile()
  
	# Determine if we are clocking in or out
	clockState = getClockState()
	
	# Try to get command from argument
	action = getArgument()
		
	# TODO: Make a way to subtract time from clock in or out (clock in or clock out earlier than NOW)
	if action == clockState or action[0] == clockState[0] or action == 'CLOCK' or action[0] == 'C':
		clockCommand(clockState)
	elif action == ' ':
		# Ran with no arguments
		statusCommand()
	else:
		if action[0] != '?':
			print('Unknown command.')
		printUsage()
