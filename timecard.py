#!/usr/bin/python3

###########################################################################################
# Stephen-Hamilton-C - Licensed under the GNU GPL v3 License.
# Source code can be found at https://github.com/Stephen-Hamilton-C/Timecard
# Place this script anywhere, and modify .bashrc so it runs this script with the auto arg.
# e.g. `python3 ~/timecard/timecard.py auto`
###########################################################################################

# TODO: For release:
#	- Do this for exact times and not just offset minutes
#   - Update checking
# TODO: Post-release:
# 	- Make an i3 status command

import sys, os, stat, json, time
from datetime import date, datetime
from platform import system
from shutil import move

class Version:
	def __init__(self, versionStr) -> None:
		version = versionStr.split('.')
		self.major = int(version[0])
		self.minor = int(version[1])
		self.patch = int(version[2])
		self.number = self.major*100 + self.minor*10 + self.patch

# Setup constants
VERSION: Version = Version('0.0.0')
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

# Check for updates
try:
	import requests
	try:
		versionRequest = requests.get('https://raw.githubusercontent.com/Stephen-Hamilton-C/Timecard/main/version.txt')
		versionRequest.raise_for_status()
		latestVersion = Version(versionRequest.text)
		currentVersion = Version(VERSION)
		if latestVersion.number > currentVersion.number:
			print('An update is available for timecard.py!')
	except requests.exceptions.RequestException:
		print('Unable to get latest version string! Are you online?')
except ImportError:
	print('Timecard: Unable to check for updates! To get automatic updates, run `sudo pip3 install requests`')

def readFile():
	global timeEntries
	with open(TIMECARD_FILE, 'r') as timecardFile:
		timecardData: str = timecardFile.read()
		timeEntries = json.loads(timecardData)

def saveFile():
	with open(TIMECARD_FILE, 'w') as timecardFile:
		timeEntriesJson: str = json.dumps(timeEntries)
		timecardFile.write(timeEntriesJson)
  
def clockIn(clockedTime):
    newEntry: dict[str, int] = { "startTime": round(clockedTime), "endTime": 0 }
    timeEntries.append(newEntry)
    
def clockOut(clockedTime):
    lastEntry: dict[str, int] = timeEntries[-1]
    lastEntry['endTime'] = round(clockedTime)
    
def getClockState() -> str:
    # Clock state needs data to be loaded	
	if len(timeEntries) == 0:
		try:
			readFile()
		except FileNotFoundError:
			return 'IN'
	if timeEntries[-1]['endTime'] == 0:
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
			timeSum += timeEntries[i+1]['startTime'] - timeEntry['endTime']
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

    
def clockCommand():
	clockState = getClockState()
	# TODO: Test that offset clocking in/out works
	clockTime = time.time()
	if getArgument(2) != ' ':
		try:
			offset = int(getArgument(2))
			clockTime -= offset*60
		except ValueError:
			print('Offset could not be parsed as a number! Use `timecard help` to see usage of this command.')
			return
	if clockState == 'IN':
		if len(timeEntries) > 0 and timeEntries[-1]['endTime'] == 0:
			print('Already clocked in! It seems another instance of timecard.py was running...')
			return
		clockIn(clockTime)
		remainingTimeCommand()
		if len(timeEntries) > 0:
			totalBreakTimeCommand()
	elif clockState == 'OUT':
		if timeEntries[-1]['endTime'] != 0:
			print('Already clocked out! It seems another instance of timecard.py was running...')
			return
		clockOut(clockTime)
		hoursWorkedCommand()
	print('Clocked ' + clockState.lower() + ' at ' + datetime.fromtimestamp(clockTime).strftime('%H:%M'))
	saveFile()
 
def hoursWorkedCommand():
	timeSum: int = getTotalTimeWorked()

	# Calculate the nearest quarter hour to input into a timesheet database
	totalTime = time.gmtime(timeSum)
	nearestQuarterHour = totalTime.tm_hour + (round(totalTime.tm_min/15) * 15) / 60

	# Format the time
	formattedTime = time.strftime(getFormatter(timeSum), totalTime)

	# Report to the user the results
	print('Total time worked:')
	print(formattedTime)
	print(str(nearestQuarterHour) + ' hours')
	print()

def totalBreakTimeCommand():
	timeSum: int = getTotalBreakTime()
	totalTime = time.gmtime(timeSum)

	formattedTime = time.strftime(getFormatter(timeSum), totalTime)

	print('Total time on break:')
	print(formattedTime)
	print()

def statusCommand():
	for i in range(len(timeEntries)):
		timeEntry = timeEntries[i]
		formattedStartTime = datetime.fromtimestamp(timeEntry['startTime']).strftime('%H:%M')
		formattedEndTime = datetime.fromtimestamp(timeEntry['endTime']).strftime('%H:%M')
		if i == 0:
			print('Started work at '+formattedStartTime)
		else:
			print('Clocked in: '+formattedStartTime)
		if(timeEntry['endTime'] != 0):
			print('Clocked out: '+formattedEndTime)
		else:
			print('Time since clocked in: '+datetime.fromtimestamp(time.time() - timeEntry['startTime']).strftime('%H:%M'))
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
			bashrcFile = open(bashrcPath, 'a')
			exePath = os.path.join(INSTALL_DIR, 'timecard')

			# Move timecard.py to install dir
			move(SCRIPT_PATH, exePath)

			# Append to bashrc
			bashrcFile.write('\n# Timecard autorun\n')
			bashrcFile.write('python3 ' + exePath + ' auto #timecard\n')
			try:
				# Set timecard.py to rwx by user
				os.chmod(exePath, stat.S_IRWXU)

				# Set PATH to include .local/bin, if not already
				PATH = os.getenv('PATH')
				if PATH.find('.local/bin') == -1:
					pathPrompt = input('Do you want to add ~/.local/bin to your PATH? This will allow you to run timecard like a command. (Y/n): ').strip().upper()
					if pathPrompt != 'n':
						bashrcFile.write('PATH=$PATH:~/.local/bin #timecard\n')
					else:
						# If user doesn't want to set path, we can try an alias
						aliasPrompt(bashrcPath, exePath)
			except Exception:
				# Probably couldn't set timecard.py to be rwx. We could use an alias tho
				print('Unable to make timecard.py executable! You\'ll have to use `python3 timecard.py` to run Timecard.')
				aliasPrompt(bashrcPath, exePath)
			bashrcFile.write('\n')
			print('Installed to ' + INSTALL_DIR + '. Ensure that is in your PATH and then use `timecard` to run the script')
			bashrcFile.close()


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
		print('timecard.py has been uninstalled!')
		os.remove(SCRIPT_PATH)
	else:
		print('timecard.py is not installed!')

def getArgument(argIndex = 1) -> str:
	if len(sys.argv) > argIndex:
		return sys.argv[argIndex].strip().upper()
	return ' '

def printVersion():
	print('timecard.py version ' + VERSION)
	if latestVersion != None and latestVersion['number'] > currentVersion['number']:
		print('An update is available! New version: ' + versionRequest.text)

def printUsage():
	print('\ntimecard.py commands:')
	print('	<no command> - Shows time log, how many hours worked, how much time you have left to meet your desired hours worked ('+str(EXPECTED_WORK_HOURS / 60 / 60)+' hours), and how many hours you\'ve been on break.')
	print('	Install - Installs timecard.py to the user folder, adds an autorun to .bashrc, and adds ~/.local/bin to PATH if necessary.')
	print('	Uninstall - Removes timecard.py from system.')
	print('	IN (I) [offset] - Clocks in if you aren\'t already. If an offset is supplied, it logs you as clocked in OFFSET minutes ago.')
	print('	OUT (O) [offset] - Clocks out if you aren\'t already. If an offset is supplied, it logs you as clocked out OFFSET minutes ago.')
	print('	CLOCK (C) [offset] - Automatically determines whether to clock in/out. See IN and OUT commands.')
	print('	Version (V) - Prints the current version of timecard.py.')
	print('	Help | ? - Prints this help message.')
	print()

def isCommandOrAlias(action, cmd):
	return action == cmd or action[0] == cmd[0]



# Check for this first so that we aren't prompting the user about clocking in if all they want to do is install
if getArgument() == 'INSTALL':
	installCommand()
elif getArgument() == 'UNINSTALL':
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
		clockCommand()
		
elif getArgument() == 'AUTO':
    # Script was run automatically by .bashrc (if configured that way) and timecard already exists
	print('Timecard already present for today. If you need to clock ' + getClockState().lower() + ', run `python3 '+__file__+'`')
else:
	readFile()
  
	# Try to get command from argument
	action = getArgument()
		
	if isCommandOrAlias(action, 'CLOCK'):
		clockCommand()
	elif isCommandOrAlias(action, 'IN'):
		if getClockState() == 'OUT':
			print('You\'re already clocked in! Use `timecard out` to clock out first.')
		else:
			clockCommand()
	elif isCommandOrAlias(action, 'OUT'):
		if getClockState() == 'IN':
			print('You\'re already clocked out! Use `timecard in` to clock in first.')
		else:
			clockCommand()
	elif isCommandOrAlias(action, 'VERSION'):
		printVersion()
	elif action == ' ':
		# Ran with no arguments
		statusCommand()
	else:
		if action[0] != '?' and action != 'HELP':
			print('Unknown command.')
		printUsage()
