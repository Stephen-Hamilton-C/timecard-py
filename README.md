# Timecard.py <!-- omit in toc -->
A simple timecard command line python script. Written by a developer, for developers. It can be configured to automatically run when you open a terminal, making this ideal for our terminal-heavy workspace. Making sure you never forget to clock in.

# Table of Contents <!-- omit in toc -->

- [Installing](#installing)
  - [Automatic Install](#automatic-install)
  - [Manual Install - Linux](#manual-install---linux)
- [Uninstalling](#uninstalling)
  - [Automatic Uninstall](#automatic-uninstall)
  - [Manual Uninstall - Linux](#manual-uninstall---linux)
- [Command Usage](#command-usage)
- [Data Files](#data-files)
- [License](#license)

# Installing

## Automatic Install
- Run `python3 timecard.py install`. This will perform the following:
    1. Move `timecard.py` to `~/.local/bin/` and remove the `.py` extension
    1. Add a line to .bashrc that will run `timecard auto`
    1. Attempt to give `timecard` executable permissions
        - If this fails, timecard will alert you and prompt if you want to add an alias instead
    2. Check if you already have `~/.local/bin` in your PATH. If not, it will prompt if you want to add it.
        - If you answer no, timecard will prompt if you want to add an alias instead
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

# Command Usage

TODO: Write this

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