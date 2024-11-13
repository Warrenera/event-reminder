# event-reminder
A simple Python script to help me remember my family's birthdays and other dates I'll get in trouble for not remembering

## Configurations
### Required Configurations
#### events.csv
This is a list of static events that will be parsed by events.py. Events need to be added here prior to script execution. Events are in `<MM>-<DD>,<event descripton>` format.

#### varying_values.ini
This is a list of dynamic events that will be parsed by events.py. Events need to be added here prior to script execution. MM-DD values for last Mother's and Father's Days are present in the file by default.

### Optional Configurations
#### events.bat
This batch file runs events.py on Windows startup when placed in the Windows 10 startup folder. The default location for events.py in events.bat is `C:\Repositories\event-reminder\events.py`. This file path should be changed to wherever the script is stored locally on your machine.

## Usage
Run events.py using `python events.py <[-fp | --filepath] C:\alternate\path\to\events.csv>`.

### Command Line Arguments
#### -e | --events
Optional: the path to an alternate location for the events CSV file if different from the default repository filepath.
#### -v | --varying_values
Optional: the path to an alternate location for the varying values configuration file if different from the default repository filepath.
