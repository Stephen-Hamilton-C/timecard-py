# Timecard <!-- omit in toc -->
A simple timecard command line python script. Written by a developer, for developers. It can be configured to automatically run when you open a terminal, making this ideal for our terminal-heavy workspace. Making sure you never forget to clock in.

# Table of Contents <!-- omit in toc -->

- [Features](#features)
- [Command Usage](#command-usage)
- [Installing](#installing)
  - [Requirements](#requirements)
  - [Automatic Install](#automatic-install)
  - [Manual Install - Linux](#manual-install---linux)
- [Uninstalling](#uninstalling)
  - [Automatic Uninstall](#automatic-uninstall)
  - [Manual Uninstall - Linux](#manual-uninstall---linux)
- [Data Files](#data-files)
- [License](#license)

# Features

- Clock in and out at any time of the day.
- Reports how many hours you've been working.
- Coveniently gives hours worked rounded to nearest quarter.
- Reports how long you've been on break.
- Estimates when you'll be done with work, presuming an 8 hour work day and no breaks.
- Locks up terminal until you have clocked in for the first time that day (only if installed).
- Automatic cleanup. Ensures your drive won't get filled with useless timecard data.
- i3status text. Run `timecard i3status` and it will return how many hours worked to the nearest quarter, or how long you've been on break, depending on if you are clocked in or not.
- Automatic update checking (requires `requests` to be installed)

# Command Usage

`timecard [command]`
- `<no args>`: Shows time log, how many hours worked, how much time left until you're done, and how many hours you've been on break.
- `install`: Installs timecard to the user folder. See [Automatic Install](#automatic-install) for exactly what this does.
- `uninstall`: Removes timecard from the system.
- `in [offset]` (alias `i`): Clocks in if you haven't already.
  - If offset is supplied as an integer, it will clock in `[offset]` minutes ago.
  - If offset is supplied as a 24-hour time (e.g. 17:31), it will clock in at that time.
  - If no offset is supplied, it will clock in now.
- `out [offset]` (alias `o`): Clocks out if you haven't already.
  - See `in` for offset usage.
- `clock [offset]` (alias `c`): Clocks in or out, depending on current timecard state.
  - See `in` for offset usage.
- `undo` (alias `u`): Undos the last clock in/out action.
- `update`: Updates timecard to the latest version
- `version` (alias `v`): Prints the current version of timecard.
- `help` or `?`: Prints out a help message explaining command usage

# Installing

## Requirements
- Python 3 or later
- (optional) requests installed via pip3. Used for automatic updates.

## Automatic Install
- Run `python3 timecard.py install`. This will perform the following:
    1. Move `timecard.py` to `~/.local/bin/` and remove the `.py` extension
    2. Add a line to .bashrc that will run `timecard auto`
    3. Attempt to give `timecard` executable permissions
        - If this fails, timecard will alert you and prompt if you want to add an alias instead
    4. Check if you already have `~/.local/bin` in your PATH. If not, it will prompt if you want to add it.
        - If you answer no, timecard will prompt if you want to add an alias instead
    5. Run `sudo pip3 install requests` for automatic updates
- Now you can run `timecard`

## Manual Install - Linux
1. Place `timecard.py` somewhere memorable.
2. Run `chmod u+x timecard.py` so it can be executed.
3. Add the script's parent folder to your PATH. Alternatively, you could run `sudo ln -s /path/to/timecard.py /usr/bin/timecard` so you don't have to update your PATH.
    - If you do update your PATH, I recommend removing the `.py` extension so you don't have to type that out every time.
    - One more alternative is making an alias to the script in your .bashrc: `alias timecard="python3 /path/to/timecard.py"`. You wouldn't need to change file permissions or modify your PATH this way.
4. Run `timecard`.

# Uninstalling

## Automatic Uninstall
1. Run `timecard uninstall`.

## Manual Uninstall - Linux
1. Delete the `timecard.py` file and any symlinks you may have made.
2. Run `rm -rfv ~/.local/share/timecard/`.
3. Edit your .bashrc (`nano ~/.bashrc`) and find and remove the line under the `# Timecard autorun` comment.

# Data Files
Timecard.py creates timecard.json files to keep track of your clocked time. In Linux, these can be found in `~/.local/share/timecard/`. In Windows, they're in `%LocalAppData%\timecard\`.
Timecard.py automatically cleans out any timecard.json files that are a week old each time it is run. It will report when a timecard.json file is deleted.
The timecard.json files are stored in UNIX Epoch seconds. Their structure is as so:
```
[
    {
        "startTime": 1234567890,
        "endTime": 1234567891
    },
    {
        "startTime": 1642739286,
        "endTime": 0
    }
]
```
If the user has not clocked out yet, the last endTime is always 0.

# License
timecard.py is licensed under the GNU General Public License v3.0. You can find the license details in the [LICENSE](https://github.com/Stephen-Hamilton-C/timecard/blob/main/LICENSE) file in the main branch. Feel free to repurpose, redistribute, and branch off this code anytime. Just keep your modifications open source and licensed the same way :D