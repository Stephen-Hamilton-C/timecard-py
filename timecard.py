#!/usr/bin/python3

###########################################################################################
# Stephen-Hamilton-C - Licensed under the GNU GPL v3 License.
# Source code can be found at https://github.com/Stephen-Hamilton-C/timecard
# Run `python3 timecard install` to automagically install this script into your system.
# Also install requests with `sudo pip3 install requests` for automatic update checking.

# If you fork this project, change the below constant to `<username>/<repo>`.
# If you don't, update checking and getting will come from my repo.
GITHUB_REPO = 'Stephen-Hamilton-C/timecard'
###########################################################################################

import sys, os, stat, json, time
from datetime import date, datetime
from platform import system
from shutil import move

# TODO: Test automatic updating
# TODO: Update README to account for built versions
# TODO: Update installation instructions in RELEASE

class Version:
	def __init__(self, versionStr) -> None:
		version = versionStr.split('.')
		self.major = int(version[0])
		self.minor = int(version[1])
		self.patch = int(version[2])
		self.number = self.major*100 + self.minor*10 + self.patch

	def __str__(self) -> str:
		return str(self.major)+'.'+str(self.minor)+'.'+str(self.patch)

# Setup constants
VERSION: Version = Version('1.1.0')
SCRIPT_PATH = os.path.realpath(__file__)
EXPECTED_WORK_HOURS: int = 8 * 60 * 60
TIMECARD_FILE: str = 'timecard.' + str(date.today()) + '.json'
TIMECARD_PATH: str = os.path.expanduser('~/.local/share/timecard')
# TIMECARD_PATH: str = os.path.dirname(SCRIPT_PATH)
INSTALL_DIR: str = os.path.expanduser('~/.local/bin')
if system() == 'Windows':
	TIMECARD_PATH = os.path.expanduser('~\\AppData\\Local\\timecard')
	INSTALL_DIR = os.path.expanduser('~')

# Ensure cwd is timecard dir
if not os.path.exists(TIMECARD_PATH):
	os.makedirs(TIMECARD_PATH)
os.chdir(TIMECARD_PATH)

latestVersion = None
isInstalled = os.path.exists(os.path.join(INSTALL_DIR, 'timecard.py')) or os.path.exists(os.path.join(INSTALL_DIR, 'timecard')) or os.path.exists(os.path.join(INSTALL_DIR, 'timecard.exe'))
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
	clockTime = time.time()
	if getArgument(2) != ' ':
		try:
			# Try parsing as just minutes
			offset = int(getArgument(2))
			clockTime -= offset*60
		except ValueError:
			try:
				# Try parsing as 24-hour time
				offsetTime = datetime.strptime(getArgument(2), '%H:%M')
				offsetDate = datetime.now().replace(hour=offsetTime.hour, minute=offsetTime.minute, second=0)
				offsetTimestamp = offsetDate.timestamp()

				# Sanity check
				if offsetTimestamp > clockTime:
					print('Offset cannot be after current time! Use `timecard help` to see usage of this command.')
					return

				offset = clockTime - offsetTimestamp
				clockTime -= offset
			except ValueError:
				print('Offset could not be parsed! Use `timecard help` to see usage of this command.')
				return
	if clockState == 'IN':
		# Sanity check
		if len(timeEntries) > 0 and clockTime < timeEntries[-1]['endTime']:
			print('Offset cannot be before last clock out time! Use `timecard help` to see usage of this command.')
			return
		# Check that we aren't already clocked in
		if len(timeEntries) > 0 and timeEntries[-1]['endTime'] == 0:
			print('Already clocked in! It seems another instance of timecard was running...')
			return

		clockIn(clockTime)
		remainingTimeCommand()
		if len(timeEntries) > 0:
			totalBreakTimeCommand()
	elif clockState == 'OUT':
		# Sanity check
		if clockTime < timeEntries[-1]['startTime']:
			print('Offset cannot be before last clock in time! Use `timecard help` to see usage of this command.')
			return
		# Check that we aren't already clocked out
		if timeEntries[-1]['endTime'] != 0:
			print('Already clocked out! It seems another instance of timecard was running...')
			return

		clockOut(clockTime)
		hoursWorkedCommand()
	print('Clocked ' + clockState.lower() + ' at ' + datetime.fromtimestamp(clockTime).strftime('%H:%M'))
	saveFile()

def getNearestQuarterHour(totalTime):
	return totalTime.tm_hour + (round(totalTime.tm_min/15) * 15) / 60

def hoursWorkedCommand():
	timeSum: int = getTotalTimeWorked()

	# Calculate the nearest quarter hour to input into a timesheet database
	totalTime = time.gmtime(timeSum)
	nearestQuarterHour = getNearestQuarterHour(totalTime)

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
			timeSum = time.time() - timeEntry['startTime']
			totalTime = time.gmtime(timeSum)
			print('Time since last clocked in: '+time.strftime(getFormatter(timeSum), totalTime))
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
		print('timecard is already installed!')
	else:
		if not os.path.exists(INSTALL_DIR):
			os.makedirs(INSTALL_DIR)

		if system() == 'Windows':
			move(SCRIPT_PATH, os.path.join(INSTALL_DIR, __file__))
			print('Installed timecard v'+str(VERSION)+' to ' + INSTALL_DIR + '. Use `python3 '+__file__+'` to run the script')
		else:
			bashrcPath = os.path.expanduser('~/.bashrc')
			bashrcFile = open(bashrcPath, 'a')
			exePath = os.path.join(INSTALL_DIR, 'timecard')

			# Move timecard to install dir
			move(SCRIPT_PATH, exePath)

			# Append to bashrc
			bashrcFile.write('\n# Timecard autorun\n')
			bashrcFile.write('python3 ' + exePath + ' auto #timecard\n')
			try:
				# Set timecard to rwx by user
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
				# Probably couldn't set timecard to be rwx. We could use an alias tho
				print('Unable to make timecard executable! You\'ll have to use `python3 timecard` to run Timecard.')
				aliasPrompt(bashrcPath, exePath)
			bashrcFile.write('\n')
			print('Installed timecard v'+str(VERSION)+' to ' + INSTALL_DIR + '. Ensure that is in your PATH and then use `timecard` to run the script')
			try:
				import requests
			except ImportError:
				sudo = 'sudo '
				if system() == 'Windows':
					sudo = ''
				print('Also run `'+sudo+'pip3 install requests` for automatic update checking.')
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
		print('timecard v'+str(VERSION)+' has been uninstalled!')
		os.remove(SCRIPT_PATH)
	else:
		print('timecard is not installed!')

def undoCommand():
	clockState = getClockState()
	if clockState == 'IN':
		timeEntries[-1]['endTime'] = 0
		print('Undo clock out. Currently clocked in.')
	elif clockState == 'OUT':
		timeEntries.pop(-1)
		print('Undo clock in. Currently clocked out.')

	if len(timeEntries) > 0:
		saveFile()
	elif os.path.exists(TIMECARD_FILE):
		os.remove(TIMECARD_FILE)

def getArgument(argIndex = 1) -> str:
	if len(sys.argv) > argIndex:
		return sys.argv[argIndex].strip().upper()
	return ' '

def printVersion():
	print('timecard version ' + str(VERSION))

def updateCommand():
	if checkForUpdates(False):
		import requests

		# Go to script directory
		scriptDir = os.path.dirname(SCRIPT_PATH)
		scriptName = os.path.basename(SCRIPT_PATH)
		os.chdir(scriptDir)

		# Prompt user on which platform to get. Defaulting to built.
		print('Timecard comes in two different platforms - the raw Python script, or a built executable.')
		print('Usually you want to use the raw Python script, but if you don\'t have Python3 installed, the built version is usually what you want.')
		print('If you are uncertain, just go with `built`.')
		timecardTypePrompt = input('Which platform of Timecard do you want? (py/BUILT): ')
		timecardType = '.exe' if system() == 'Windows' else ''
		if timecardTypePrompt.upper()[0] == 'P':
			timecardType = '.py'

		# Download new version and write to a .new file
		print('Downloading timecard'+timecardType+'...')
		newTimecardName = 'timecard'+timecardType
		updateRequest = requests.get('https://github.com/'+GITHUB_REPO+'/releases/download/v'+str(latestVersion)+'/'+newTimecardName)
		updateRequest.raise_for_status()
		open(newTimecardName+'.new', 'wb').write(updateRequest.content)

		# Replace current file with new file
		print('Updating timecard to v'+str(latestVersion)+'...')
		os.rename(SCRIPT_PATH, scriptDir+'timecard.old')
		if timecardType == '.exe':
			scriptName = 'timecard.exe'
		os.rename(newTimecardName+'.new', scriptName)

		# Notify the user and delete this file
		print('Timecard has been updated!')
		os.remove(__file__)

def checkForUpdates(alertUser = True):
	# Try to import requests
	try:
		import requests
		try:
			# Try to get latest version
			versionRequest = requests.get('https://raw.githubusercontent.com/'+GITHUB_REPO+'/main/version.txt')
			versionRequest.raise_for_status() # Throw a RequestException if file is not found (maybe not online)
			latestVersion = Version(versionRequest.text)

			# Notify user of new update if one is available
			if latestVersion.number > VERSION.number:
				if alertUser:
					print('----------------------------------------------------------------')
					print('An update is available for timecard!')
					print('Current version: '+str(VERSION)+', new version: '+str(latestVersion)+'.')
					print('Go to https://github.com/'+GITHUB_REPO+'/releases/latest or run `timecard update` to download the update.')
					print('----------------------------------------------------------------')
					print()
				return True
		except requests.exceptions.RequestException:
			pass
	except ImportError:
		# Requests is not installed, notify user
		sudo = 'sudo '
		if system() == 'Windows':
			sudo = ''
		print('Timecard: Unable to check for updates! To get automatic updates, run `'+sudo+'pip3 install requests`')
	return False

def printUsage():
	print('\ntimecard commands:')
	print('	<no command> - Shows time log, how many hours worked, how much time you have left to meet your desired hours worked ('+str(EXPECTED_WORK_HOURS / 60 / 60)+' hours), and how many hours you\'ve been on break.')
	print('	Install - Installs timecard to the user folder, adds an autorun to .bashrc, and adds ~/.local/bin to PATH if necessary.')
	print('	Uninstall - Removes timecard from system.')
	print('	IN (I) [offset] - Clocks in if you aren\'t already. If an offset is supplied, it logs you as clocked in OFFSET minutes ago or at OFFSET time. Time must be formatted in 24-hour time. (e.g. 17:31)')
	print('	OUT (O) [offset] - Clocks out if you aren\'t already. If an offset is supplied, it logs you as clocked out OFFSET minutes ago or at OFFSET time. Time must be formatted in 24-hour time. (e.g. 17:31)')
	print('	CLOCK (C) [offset] - Automatically determines whether to clock in/out. See IN and OUT commands.')
	print('	UNDO (U) - Undos the last clock in/out action')
	print('	Update - Updates timecard to latest version if one is available.')
	print('	Version (V) - Prints the current version of timecard.')
	print('	Help | ? - Prints this help message.')
	print()

def isCommandOrAlias(action, cmd):
	return action == cmd or (len(action) == 1 and action[0] == cmd[0])




# Check for this first so that we aren't prompting the user about clocking in if all they want to do is install
if getArgument() == 'INSTALL':
	installCommand()
elif getArgument() == 'UNINSTALL':
	uninstallCommand()
elif getArgument() == 'I3STATUS':
	if not os.path.exists(TIMECARD_FILE):
		print('OUT')
	else:
		if getClockState() == 'IN':
			breakTime: int = getTotalBreakTime()
			totalTime = time.gmtime(breakTime)
			formattedTime = time.strftime(getFormatter(breakTime), totalTime)
			print('OUT: ' + formattedTime)
		else:
			print('IN: ' + str(getNearestQuarterHour(time.gmtime(getTotalTimeWorked()))))
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
	elif isCommandOrAlias(action, 'UNDO'):
		undoCommand()
	elif action == 'UPDATE':
		updateCommand()
	elif isCommandOrAlias(action, 'VERSION'):
		printVersion()
	elif action == ' ':
		# Ran with no arguments
		statusCommand()
	else:
		if action[0] != '?' and action != 'HELP':
			print('Unknown command.')
		printUsage()

if getArgument() != 'I3STATUS' or getArgument() != 'UPDATE':
	checkForUpdates()

	# Cleanup old timecards, if any
	for timeFile in os.listdir():
		if os.path.isfile(timeFile) and timeFile.startswith('timecard.') and timeFile.endswith('.json') and os.stat(timeFile).st_mtime < time.time() - 7*60*60*24:
			print('Removing old timecard: '+timeFile)
			os.remove(timeFile)