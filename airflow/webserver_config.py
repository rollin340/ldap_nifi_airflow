import os
from flask_appbuilder.security.manager import AUTH_LDAP

AUTH_TYPE = AUTH_LDAP
AUTH_LDAP_SERVER = 'ldap://openldap:1389'
AUTH_LDAP_USE_TLS = False

AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Public"
AUTH_LDAP_FIRSTNAME_FIELD = "givenName"
AUTH_LDAP_LASTNAME_FIELD = "sn"
AUTH_LDAP_EMAIL_FIELD = "mail"

AUTH_LDAP_SEARCH = 'ou=people,dc=example,dc=org'
AUTH_LDAP_UID_FIELD = "cn"

AUTH_LDAP_BIND_USER = 'cn=admin,dc=example,dc=org'
AUTH_LDAP_BIND_PASSWORD = 'adminpassword'

# Automatic mapping of groups to Airflow permissions
# 
# To create custome groups, copy 'User', and remove 
# general DAG permissions, and add for specific tags
# 
# Change the target permissions group once done
#
AUTH_ROLES_MAPPING = {
    'cn=users,ou=groups,dc=example,dc=org': ['User'],
    'cn=admins,ou=groups,dc=example,dc=org': ['Admin'],
}

AUTH_LDAP_GROUP_FIELD = "memberOf"

AUTH_ROLES_SYNC_AT_LOGIN = True
PERMANENT_SESSION_LIFETIME = 1800