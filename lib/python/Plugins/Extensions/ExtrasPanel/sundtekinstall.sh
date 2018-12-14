#!/bin/sh

if [ -e "/tmp/sundtek_netinst.sh" ]; then
    #installer script already exits
    #so we remove it
    rm -rf /tmp/sundtek_netinst.sh
fi
    ## install net-development driver
    cd /tmp
    wget http://sundtek.de/media/sundtek_netinst.sh
    chmod 755 sundtek_netinst.sh
    /tmp/sundtek_netinst.sh -keepalive -easyvdr
