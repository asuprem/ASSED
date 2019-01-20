# LITMUS
This directory contains scripts for LITMUS (updated).

Details will be added over time. Please read `initialize.md` for initializatioon/setup details.

Please read `Code Steps.md` for details on how LITMUS functions.


# Configuration
`config.json` contains the configuration file for LITMUS, along with all passwords, etc

# MYSQL Access
Start the mysql server with

    sudo /etc/init.d/mysqld  start

Access the mysql server with 

    > mysql -h 127.0.0.1 -P 3306 -u grait-dm -p
    > Lr1eUDc(f4Hi

The format is:

    mysql -h HOST -P PORT_NUMBER -u USERNAME -p

The config file is located at `/etc/my.cnf`. The socket is located at `/var/lib/mysql/mysql.sock`.

## MYSQL DB
All our work is done on the LITMUS database in mysql. Use `use LITMUS` when logging in to switch to the correct database

# Redis Access

## Redis DB


#  Default CRON

    # HEADER: This file was autogenerated at Tue Apr 07 00:06:54 -0400 2015 by puppet.
    # HEADER: While it can still be managed manually, it is definitely not recommended.
    # HEADER: Note particularly that the comments starting with 'Puppet Name' should
    # HEADER: not be deleted, as doing so could cause duplicate cron jobs.
    # Puppet Name: check_ntp
    13 3 * * * if ! /usr/local/bin/check_ntp; then /sbin/service ntpd stop; /usr/sbin/ntpdate -b ntp1.gatech.edu ntp2.gatech.edu; /sbin/service ntpd start; fi
    */15 * * * * /aibek/venv/bin/python /aibek/download_physical.py > /aibek/download_physical.out 2>&1
    */15 * * * * sh /aibek/download_twitter_jap.sh
    */15 * * * * sh /aibek/download_twitter.sh
    */1 * * * * sh /aibek/download_news_twitter.sh
    */20 * * * * sh /aibek/download_news.sh
    #/aibek/venv/bin/python news_download.py
    */5 * * * * sh /aibek/web_server.sh
    #*/5 * * * * sh /aibek/cron_test.sh > /aibek/cron_test.out
    */10 * * * * /aibek/venv/bin/python /aibek/current_download.py > /aibek/current_download.out 2>&1
    */20 * * * * /aibek/venv/bin/python /aibek/download_youtube_current.py > /aibek/download_youtube_current.out 2>&1
    */20 * * * * /bin/bash /aibek/current_loc.sh
    */20 * * * * /aibek/venv/bin/python /aibek/current_geo.py > /aibek/current_geo.out 2>&1
    */20 * * * * /aibek/venv/bin/python /aibek/physical_geo.py > /aibek/physical_geo.out 2>&1
    */20 * * * * /aibek/venv/bin/python /aibek/current_lstop.py > /aibek/current_lstop.out 2>&1
    */20 * * * * /aibek/venv/bin/python /aibek/current_classify.py > /aibek/current_classify.out 2>&1
    #*/20 * * * * /usr/bin/java -jar /aibek/w2v_unlabeled.jar > /aibek/w2v_unlabeled_java.out 2>&1
    #0 * * * * /aibek/venv/bin/python /aibek/current_rest.py > /aibek/current_rest.out 2>&1
    # 0 * * * * /aibek/venv/bin/python /aibek/download_instagram.py > /aibek/download_instagram.out 2>&1
    @daily sh /aibek/download_fb.sh
    @daily /aibek/venv/bin/python /aibek/current_analyze1.py > /aibek/current_analyze.out 2>&1
    @daily /aibek/venv/bin/python /aibek/checkFeeds.py > /aibek/checkFeeds.out 2>&1
    @daily /aibek/venv/bin/python /aibek/prune.py > /aibek/prune.out 2>&1
    # Puppet Name: puppet
    13 * * * * /usr/bin/puppet agent --onetime --no-daemonize > /dev/null 2>&1

