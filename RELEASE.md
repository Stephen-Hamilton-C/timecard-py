Initial release of timecard.py! I can now *finally* say I've fully released a finished product. If you find any bugs, create an issue describing the problem in full.

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

# Installation Instructions
See the [README](https://github.com/Stephen-Hamilton-C/timecard/blob/main/README.md) for specific instructions - or just run `python3 timecard.py install`