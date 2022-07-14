# Add MemberOf Module
ldapadd -Q -Y EXTERNAL -H ldapi:/// -f /tmp/memberof_config.ldif
ldapmodify -Q -Y EXTERNAL -H ldapi:/// -f /tmp/refint1.ldif
ldapadd -Q -Y EXTERNAL -H ldapi:/// -f /tmp/refint2.ldif

# Clean tree
ldapdelete -x -r -H ldap://openldap:1389 -D "cn=admin,dc=example,dc=org" -w adminpassword "dc=example,dc=org"

# Re-add initial users
ldapadd -x -H ldap://openldap:1389 -D cn=admin,dc=example,dc=org -w adminpassword -f /ldifs/initial_users.ldif 

# Confirm results
ldapsearch -x -H ldap://openldap:1389 -b "dc=example,dc=org" memberOf
