#! /bin/bash

installSoftware() {
    apt -qq -y install python3-flask python3-click uwsgi-plugin-python3 python3-pip nginx git
}

installMyBookmarks() {
    mkdir -p /var/log/uwsgi
    pip3 install -e git+https://github.com/sunshineplan/MyBookmarks.git#egg=bookmark --src /var/www
}

setupsystemd() {
    cp -s /var/www/bookmark/bookmark.service /etc/systemd/system
    systemctl enable bookmark
    service bookmark start
}

writeLogrotateScrip() {
    if [ ! -f '/etc/logrotate.d/uwsgi' ]; then
        cat >/etc/logrotate.d/uwsgi <<-EOF
		/var/log/uwsgi/*.log {
		    copytruncate
		    rotate 12
		    compress
		    delaycompress
		    missingok
		    notifempty
		}
		EOF
    fi
}

createCronTask() {
	cp -s /var/www/bookmark/BackupMyBookmarks /etc/cron.monthly
    chmod +x /var/www/bookmark/BackupMyBookmarks
}

setupNGINX() {
    cp -s /var/www/bookmark/MyBookmarks.conf /etc/nginx/conf.d
    sed -i "s/\$domain/$domain/" /var/www/bookmark/MyBookmarks.conf
    service nginx reload
}

main() {
    read -p 'Please enter domain:' domain
    installSoftware
    installMyBookmarks
    setupsystemd
    writeLogrotateScrip
    createCronTask
    setupNGINX
}

main
