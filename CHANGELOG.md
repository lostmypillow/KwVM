# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Undocumented changes

## [0.0.1] - 2025-03-17
- Beta release
- Can open both VMs
- 0.0.2 will produce .desktop files on 'setup' input, build.sh for Linux, test with deployed API, better organized Python code for PySide6

## [0.0.2] - 2025-03-18
- Produces .desktop files on 'setup'
- prepare for test with deployed API


## [0.2.1] - 2025-03-19
- ONLY API CHANGES
- Finalized basic API functionality, only hard coded data
- 
## [0.0.4] - 2025-03-20
- Added supplied spice proxy instead of pve proxy
- change to production values
- 
## [0.0.5] - 2025-03-29
- Moved packages installation into "setup" in CentralController

## [0.0.6-alpha1] - 2025-03-29
- Moved package installation to start of program and added checks to avoid multiple sudo prompts

## [0.0.6-alpha2] - 2025-03-29
- Switched to pynput for keyboard shortcut detection

## [0.0.7] - 2025-03-31

### Fixed
- Fixed proxmox toggle default to closed

### Changed
- Improved Edit VM config dialog layout
- Improved VM details table layout
- Dialog box VM password input type is now text for clarity
- Changed site name

## [0.0.8] - 2025-04-02

### Added
- `customize.sh` for chroot operations in CUBIC ISO workflow
- Textual indicators that GUI is making an API call using the hostname of the PC

### Changed
- Input will now be dsiabled during API calls


## [0.1.0] - 2025-04-15

### Added
- `CHANGELOG.md` for changelog
- `build.sh` bash script for 3 jobs: 
  - build Qt binary
  - build custom Debian ISO with binary from previous step
  - burn said ISO into an USB
- `/api/sync_version.py` from KwMathConsult that syncs version between frontend and backend
- `/api/backend/version.py` from KwMathConsult that keeps the constant VERSION variable

### Changed
- Modified `build.sh` (compared to previous iteration in `customize.sh`) with full utilization of all cores to speed up all 3 jobs
- Moved `/api/backend/run.sh` to `/api/run.sh`, also added a line that runs `/api/sync_version.py`
- Updated `/api/backend/main.py` to use synced version from `/api/backend/version.py`
- `api/frontend/package.json` now has version that syncs with GUI release
- `*.spec` to `gitignore`
- All `logging.info()` calls to `print()` since I can't figure out why `~/.kwvm/app.log` doesn't appear, will fix in later minor release
- Only import needed modules from `pynput` module

### Removed
- Old `customize.sh` for CUBIC ISO workflow
- Links to READMEs in gui and api folder in `README.md`
- Splash images because I can't figure out how to make it appear during boot
- `uq_pve_vm_id` constraint from database schema since it's counting multiple NULLs as duplicates
- `gio` call to set `.desktop` as trusted. Possible bug, will fix in later minor release
