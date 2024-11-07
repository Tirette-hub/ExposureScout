#!/bin/bash
# Title: Users Information - Users
# Authors: Nathan Amorison
# Last Update: 24-09-2024
# Description: Get all users (name, uid and groups id they are in) as $uid$($name$):$gid$(,$gid$)*

cut -d":" -f1 /etc/passwd 2>/dev/null| while read i; do id $i;done 2>/dev/null | sed "s/uid=//" | sed "s/ gid=.*) groups=/:/" | sed "s/ gid=.*) groupes=/:/" | sed "s/([_A-Za-z\-]*)//2g"

# output example: 1000(user):1000,24,25,27,29