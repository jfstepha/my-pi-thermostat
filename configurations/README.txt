# Note that there is tons of stuff now defined through the web interface.
# it doesn't go into these files.
#
# Backups can be made with: sudo openhab-cli backup

sudo openhab-cli backup "backups/backup_`date +'%y%m%d%H%M%S'`.zip"

# Which can be resored with 

sudo openhab-cli restore <filename>
