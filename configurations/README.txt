# Note that there is tons of stuff now defined through the web interface.
# it doesn't go into these files.
#
# Backups can be made with: sudo openhab-cli backup

sudo openhab-cli backup "backups/backup_`date +'%y%m%d%H%M%S'`.zip"

# Which can be resored with 

sudo openhab-cli restore <filename>

# to make the .exe addin work, need to add the command to 
# /etc/openhab/misc/exec.whitelist/

# to check the size of the rrd4j database:
sudo du -sh /var/lib/openhab/persistence/rrd4j/

# to check the size of the influxdb database:
sudo du -sh /var/lib/influxdb/data/openhab_db
