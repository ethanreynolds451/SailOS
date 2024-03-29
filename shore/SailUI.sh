#!/bin/bash

# Get the directory of the bash script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Extract the base name of the bash script without the extension
BASENAME=$(basename "${BASH_SOURCE[0]}" .sh)

# Run the Python script with the same base name in the background and redirect its output to /dev/null
python3 "$DIR/$BASENAME.py" >/dev/null 2>&1 &

# Close the Terminal window without confirmation
osascript -e 'tell application "Terminal" to close (first window whose name contains "bash")' &>/dev/null