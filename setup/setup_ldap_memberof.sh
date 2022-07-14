#!/bin/sh

# Add memberOf module and recreate initial org tree
docker exec -d openldap /bin/sh /tmp/enable_memberof.sh