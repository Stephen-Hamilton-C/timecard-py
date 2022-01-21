# Timecard.py
A simple timecard command line python script. Written by a developer, for developers. It can be configured to automatically run when you open a terminal, making this ideal for our terminal-heavy workspace. Making sure you never forget to clock in.

## Installing

### Automatic Install
1. Ensure `~/.local/usr/bin` is in your PATH.
    - Run this command if it isn't: `echo "export PATH=$PATH:~/.local/usr/bin" >> ~/.bashrc`
2. Run `python3 timecard.py install` .

### Manual Install - Linux
1. Place `timecard.py` somewhere memorable.
2. Run `chmod u+x timecard.py` so it can be executed.
3. Add the script's parent folder to your PATH. Alternatively, you could run `sudo ln -s /path/to/timecard.py /usr/bin/timecard` so you don't have to update your PATH.
    - If you do update your PATH, I recommend removing the `.py` extension so you don't have to type that out every time.
4. Run `timecard`.

## Uninstalling

### Automatic Uninstall
1. Run `timecard uninstall`.

### Manual Uninstall - Linux
1. Delete the `timecard.py` file and any symlinks you may have made.
2. Run `rm -rfv ~/.local/share/timecard/`.
3. Edit your .bashrc (`nano ~/.bashrc`) and find and remove the line under the `# Timecard autorun` comment.

## Data Files
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