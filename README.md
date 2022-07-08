# Local copy to test LDAP & NiFi

## Setting up
- Import the certificate `./nifi/nifi-cert.pem` to your browser. You can skip this step, but you will required to "Accept the risks and continue" with launch of NiFi.

## Run the containers
From the Terminal, at base directory, run `docker compose up`.

### Docker images used
- `bitnami/openldap`:`2`
- `ldapaccountmanager/lam`:`stable`
- `apache/nifi`:`latest`

## LDAP Details
### Org Tree
<pre>
─── dc-example,dc=org
    │
    ├── ou=groups
    │   ├── cn=admins
    │   ├── cn=users
    │
    └── ou=users
        ├── cn=admin1
        ├── cn=users1
        └── cn=users2
</pre>

### Passwords

LDAP Administrator account is `cn=admin,dc-example,dc=org`, with the username `admin` and the password `adminpassword`.

All other users' passwords are set to `password`.

### Testing
From any of a container within the project network, run the following:

<code>ldapsearch -H ldap://openldap:1389 -x -b 'ou=people,dc=example,dc=org' -D 'cn=admin,dc=example,dc=org' -w adminpassword</code>

If successful, you should see the accounts above.


## Accessing the webpages
### LDAP Account Manager:
- http://localhost:8080
- Username: `admin`
- Password: `adminpassword`

### NiFi
- https://localhost:8443/nifi/
- Username: `<LDAP SID>`
- Password: `<LDAP Password>`

#### First use
Nifi has `admin1` set as the NiFi administrator. You are required to login as this account first to give rights to the other user accounts.

Here are some quick steps on adding `user1` for read permissions:
1. On the top right, open the menu, and click `Users`.
2. On the top right of the new window, click the add icon, and add `cn=user1,ou=people,dc=example,dc=org`.
3. Close  the window, then back to the top right menu, and lick on `Policies`.
4. On the top right on the new window, click the add icon, and add `cn=user1,ou=people,dc=example,dc=org`.
5. Note that on the top left of the same window, it is shown that you have given this user the rights to `'view the user interface'`.
6. `user1` can now lo in to NiFi, but will only have access to view the NiFi interface.

For the full steps on adding users, groups, and permissions, do refer to the [official NiFi documentiation](https://nifi.apache.org/docs/nifi-docs/html/administration-guide.html#config-users-access-policies).

## Misc & FAQ
### "Insufficient Permissions" when loggin in to NiFi
This means that the account eists, but has not been configured for any permissions within NiFi. Refer to the [first use section for NiFi](#first-use).