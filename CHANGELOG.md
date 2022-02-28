# Changelog <!-- omit in toc -->
All notable changes to timecard.py will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
timecard.py uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# Versions <!-- omit in toc -->
- [1.0.1 - 2022-02-28](#101---2022-02-28)
- [1.0.0 - 2022-02-26](#100---2022-02-26)

# 1.0.1 - 2022-02-28

## Fixed <!-- omit in toc -->

- Fixed version command causing errors due to update checking

# 1.0.0 - 2022-02-26

## Features <!-- omit in toc -->

- Clock in and out at any time of the day.
- Reports how many hours you've been working.
- Coveniently gives hours worked rounded to nearest quarter.
- Reports how long you've been on break.
- Estimates when you'll be done with work, presuming an 8 hour work day and no breaks.
- Locks up terminal until you have clocked in for the first time that day (only if installed).
- Automatic cleanup. Ensures your drive won't get filled with useless timecard data.
- i3status text. Run `timecard i3status` and it will return how many hours worked to the nearest quarter, or how long you've been on break, depending on if you are clocked in or not.
- Automatic update checking (requires `requests` to be installed)