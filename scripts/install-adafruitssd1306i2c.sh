#!/bin/bash

# Installer/Helper script for the adafruitssd1306i2c display for pwnagotchi
# Author: MD Raqibul Islam (github.com/erajtob)
#
# This will only work if your pwnagotchi is up-to-date with the current pwnagotchi repository,
# as this script just copies over some of the essential files for the libraries, if your device is missing one of the libraries or such
# it will cause your pwnagotchi to stop working, till you have those files.
# 1. Clone the pwnagotchi repo to your local machine
# 2. Copy this script into the pwnagotchi repo directory
# 3. You must have SSH access to the pwnagotchi device (https://pwnagotchi.org/getting-started/first-run-linux/index.html)
# 4. chmod +x ./install-adafruitssd1306i2c.sh
# 5. ./install-adafruitssd1306i2c.sh
#
# ******************************************************************************/
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

GREEN="\e[32m"
YELLOW="\e[33m"
RED="\e[31m"
CYAN="\e[36m"
RESET="\e[0m"

REMOTE_PATH="/usr/local/lib/python3.7/dist-packages"

# user input for username and hostname/IP
echo -e "${CYAN}Enter the following: ${RESET}"
echo -e "${CYAN}pwnagotchi username: ${RESET}"
read USERNAME
echo -e "${CYAN}hostname or IP address of the pwnagotchi: ${RESET}"
read HOST

# Check if SSH key is set up
echo -e "${YELLOW}Checking for SSH key access to remote host...${RESET}"
if ssh -o BatchMode=yes -o ConnectTimeout=5 "$USERNAME@$HOST" "exit" 2>/dev/null; then
  SSH_CMD="ssh $USERNAME@$HOST"
  SCP_CMD="scp"
  echo -e "${GREEN}SSH key access available. Proceeding without password.${RESET}"
else
  echo -e "${CYAN}SSH key not found or not working. Enter password for pwnagotchi: ${RESET}"
  read -s SSH_PASS
  echo
  SSH_CMD="sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no $USERNAME@$HOST"
  SCP_CMD="sshpass -p "$SSH_PASS" scp -o StrictHostKeyChecking=no"
fi

# Get the sudo password once
echo -e "${CYAN}Enter sudo password for pwnagotchi: ${RESET}"
read -s SUDO_PASS
echo

# List of files and directories to transfer
FILES=(
  "./pwnagotchi/ui/display.py"
  "./pwnagotchi/ui/hw/__init__.py"
  "./pwnagotchi/ui/hw/adafruitssd1306i2c.py"
  "./pwnagotchi/ui/hw/libs/adafruit/adafruitssd1306i2c/SSD1306.py"
  "./pwnagotchi/ui/hw/libs/adafruit/adafruitssd1306i2c/__init__.py"
  "./pwnagotchi/ui/hw/libs/adafruit/adafruitssd1306i2c/epd.py"
  "./pwnagotchi/utils.py"
)

# SCP over files to remote host to a temporary directory, preserving directory structure
TEMP_DIR="/tmp/adafruitssd1306i2c_temp"
echo -e "${YELLOW}Creating tmp directory on remote host.${RESET}"
$SSH_CMD "mkdir -p $TEMP_DIR" || {
  echo -e "${RED}Failed to create tmp directory on remote host${RESET}"
  exit 1
}

for FILE in "${FILES[@]}"; do
  RELATIVE_PATH=$(dirname "$FILE" | sed 's|^./||')
  echo -e "${YELLOW}Copying $FILE to remote host tmp directory.${RESET}"
  $SSH_CMD "mkdir -p $TEMP_DIR/$RELATIVE_PATH" || {
    echo -e "${RED}Failed to create directory $TEMP_DIR/$RELATIVE_PATH on remote host${RESET}"
    exit 1
  }
  $SCP_CMD "$FILE" "$USERNAME@$HOST:$TEMP_DIR/$RELATIVE_PATH/" || {
    echo -e "${RED}Failed to copy $FILE${RESET}"
    exit 1
  }
done

# Ensure the target adafruit directory and its subdirectories exist on the remote host
ADA_DIR="pwnagotchi/ui/hw/libs/adafruit"
echo -e "${YELLOW}Ensuring target directories for $ADA_DIR and subdirectories exist on remote host.${RESET}"
$SSH_CMD "echo '$SUDO_PASS' | sudo -S mkdir -p $REMOTE_PATH/$ADA_DIR && sudo -S mkdir -p $REMOTE_PATH/$ADA_DIR/adafruitssd1306i2c" || {
  echo -e "${RED}Failed to create target directories $REMOTE_PATH/$ADA_DIR and subdirectories on remote host${RESET}"
  exit 1
}

# Move other files to target directory with sudo and set ownership
for FILE in "${FILES[@]}"; do
  DIR_PATH=$(dirname "$FILE" | sed 's|^./||')
  BASENAME=$(basename "$FILE")
  echo -e "${YELLOW}Copying $BASENAME to $REMOTE_PATH/$DIR_PATH on remote host.${RESET}"
  $SSH_CMD "echo '$SUDO_PASS' | sudo -S cp $TEMP_DIR/$DIR_PATH/$BASENAME $REMOTE_PATH/$DIR_PATH && sudo chown root:staff $REMOTE_PATH/$DIR_PATH/$BASENAME" || {
    echo -e "${RED}Failed to copy $BASENAME${RESET}"
    exit 1
  }
done

# Backup and update configuration file on remote host
CONFIG_FILE="/etc/pwnagotchi/config.toml"
BACKUP_FILE="$TEMP_DIR/config.toml.bak"

# Create a backup of the configuration file
echo -e "${YELLOW}Backing up configuration file $CONFIG_FILE to $BACKUP_FILE on remote host.${RESET}"
$SSH_CMD "echo '$SUDO_PASS' | sudo -S cp $CONFIG_FILE $BACKUP_FILE" || {
  echo -e "${RED}Failed to backup configuration file${RESET}"
  exit 1
}

# Update the configuration file
echo -e "${YELLOW}Updating configuration file $CONFIG_FILE on remote host.${RESET}"
$SSH_CMD "echo '$SUDO_PASS' | sudo -S sed -i \
    -e 's/^ui\.display\.enabled = .*/ui.display.enabled = \"enable\"/' \
    -e 's/^ui\.display\.type = .*/ui.display.type = \"adafruitssd1306i2c\"/' \
    -e 's/^ui\.display\.color = .*/ui.display.color = \"black\"/' \
    -e 's/^ui\.display\.rotation = .*/ui.display.rotation = 0/' \
    $CONFIG_FILE" || {
  echo -e "${RED}Failed to update configuration file${RESET}"
  exit 1
}

# Verify the update and remove backup
echo -e "${YELLOW}Verifying the configuration update.${RESET}"
$SSH_CMD "
    grep -Eq '^ui\.display\.enabled\s*=\s*\"enable\"' $CONFIG_FILE &&
    grep -Eq '^ui\.display\.type\s*=\s*\"adafruitssd1306i2c\"' $CONFIG_FILE &&
    grep -Eq '^ui\.display\.color\s*=\s*\"black\"' $CONFIG_FILE &&
    grep -Eq '^ui\.display\.rotation\s*=\s*0' $CONFIG_FILE" || {
  echo -e "${RED}Verification failed. Restoring backup configuration file.${RESET}"
  $SSH_CMD "echo '$SUDO_PASS' | sudo -S cp $BACKUP_FILE $CONFIG_FILE" || {
    echo -e "${RED}Failed to restore configuration file from backup${RESET}"
    exit 1
  }
  exit 1
}

# Remove the temporary directory
echo -e "${YELLOW}Removing tmp directory from remote host.${RESET}"
$SSH_CMD "rm -rf $TEMP_DIR" || {
  echo -e "${RED}Failed to remove tmp directory on remote host${RESET}"
  exit 1
}
echo -e "${GREEN}Removed tmp directory.${RESET}"

# Confirm completion
echo -e "${GREEN}Files transferred, ownership set to root:staff, and configuration updated.${RESET}"
