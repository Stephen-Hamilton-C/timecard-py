# Changelog <!-- omit in toc -->
All notable changes to timecard-py will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
timecard-py uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# Versions <!-- omit in toc -->

- [1.1.3 - 2022-05-09](#113---2022-05-09)
- [1.1.2 - 2022-04-25](#112---2022-04-25)
- [1.1.1 - 2022-03-28](#111---2022-03-28)
- [1.1.0 - 2022-03-10](#110---2022-03-10)
- [1.0.1 - 2022-02-28](#101---2022-02-28)
- [1.0.0 - 2022-02-26](#100---2022-02-26)

# 1.1.3 - 2022-05-09

## Changed <!-- omit in toc -->
- Repo name from timecard to timecard-py

## Fixed <!-- omit in toc -->
- Incorrect help message for update command

# 1.1.2 - 2022-04-25

## Fixed <!-- omit in toc -->
- "Clock in for the day?" prompt showing when explicitly running `timecard in` for the first time.
- Updater not finding the Linux binary for the built version of timecard.

## Removed <!-- omit in toc -->
- Built versions of timecard. Only the python script is available now.

# 1.1.1 - 2022-03-28

## Fixed <!-- omit in toc -->
- Clocking in/out with negative minute offset logging as time in the future.

# 1.1.0 - 2022-03-10

## Added <!-- omit in toc -->
- Updating function. Run `timecard update` to automatically install latest update

## Changed <!-- omit in toc -->
- Update notification format
- Timecard now references itself as timecard rather than timecard.py
- Built versions of Timecard are now included

## Removed <!-- omit in toc -->
- Update checking in version command



# 1.0.1 - 2022-02-28

## Fixed <!-- omit in toc -->
- Version command causing errors due to update checking



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