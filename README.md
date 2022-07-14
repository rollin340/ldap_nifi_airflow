# Local copy to test LDAP & NiFi

## Steps to run the project

### Setting up
- Run `setup_airflow_permissions.sh` to create the `.env` file to ensure that files written by Airflow belongs to the host user. **Run this BEFORE you launch the containers**
- Import the certificate `./nifi/nifi-cert.pem` to your browser. You can skip this step, but you will be required to click on the "Accept the risks and continue" button with every launch of NiFi.

### Run the containers
On the Terminal from the project's root directory, run `docker compose up`.

### Enable 'memberOf' module in LDAP for Airflow
- To use Airflow, run `setup_ldap_memberof.sh`to enable LDAP to show "memberOf" details from each user. **This process recreates the initial LDAP tree, and should be done AFTER the container has started, but BEFORE new users/groups are created**

## Docker images used
- `bitnami/openldap`:`2`
- `ldapaccountmanager/lam`:`stable` AND/OR `osixia/phpldapadmin`:`latest`
- `apache/nifi`:`latest`
- `postgres`:`13`
- `redis`:`latest`
- `apache/airflow`:`2.3.3`

## LDAP Details

### Org Tree
<pre>
─── dc-example,dc=org
    │
    ├── ou=groups
    │   ├── cn=admins
    │   └── cn=users
    │
    └── ou=users
        ├── cn=admin1
        ├── cn=users1
        └── cn=users2
</pre>

### Viewing Backend Databases
From the shell terminal, run <code>ldapsearch -H ldapi:/// -Y EXTERNAL -b "cn=config" -LLL -Q "olcDatabase=*"</code>

### Enabling 'memberOf' module
By default, the 'memberOf' attribute is not enabled. Since this is needed for Airflow, the module must be loaded, and the entire tree must be re-created. [Refer to the setting up process](#enable-memberof-module-in-ldap-for-airflow) to enable this feature.

### LDAP Passwords

LDAP Administrator account is `cn=admin,dc-example,dc=org`, with the username `admin` and the password `adminpassword`.

All other users' passwords are set to `password`.

### Testing
From any of a container within the project network, run the following:

<code>ldapsearch -H ldap://openldap:1389 -x -b 'ou=people,dc=example,dc=org' -D 'cn=admin,dc=example,dc=org' -w adminpassword</code>

If successful, you should see the accounts above.


## Accessing the webpages

### LDAP Managers
There are 2 that are bundled. By default, both LAM and phpLDAPadmin are enabled. Comment/uncomment the services in the `docker-compose.yml` file according to your preferances.

#### LDAP Account Manager:
- http://localhost:8060
- Username: `admin`
- Password: `adminpassword`

#### PHP LDAP Admin:
- http://localhost:8061
- Username: `cn=admin,dc=example,dc=org`
- Password: `adminpassword`

### NiFi
- https://localhost:8443/nifi/
- Username: `<LDAP SID>`
- Password: `<LDAP Password>`

### Airflow
- http://localhost:8080
- Username: `<LDAP SID>`
- Password: `<LDAP Password>`

## NiFi details
### Adding permissions for users to login
Nifi has `admin1` set as the NiFi administrator. You are required to login as this account first to give rights to the other user accounts.

Here are some quick steps on adding `user1` for read permissions:
1. On the top right, open the menu, and click `Users`.
2. On the top right of the new window, click the add icon, and add `cn=user1,ou=people,dc=example,dc=org`.
3. Close  the window, then back to the top right menu, and lick on `Policies`.
4. On the top right on the new window, click the add icon, and add `cn=user1,ou=people,dc=example,dc=org`.
5. Note that on the top left of the same window, it is shown that you have given this user the rights to `'view the user interface'`.
6. `user1` can now lo in to NiFi, but will only have access to view the NiFi interface.

For the full steps on adding users, groups, and permissions, do refer to the [official NiFi documentiation](https://nifi.apache.org/docs/nifi-docs/html/administration-guide.html#config-users-access-policies).

#### Giving users permissions to view NiFi processes
Right-click on the Nifi canvas and select 'Manage Access Policies'. From here, you will have to create policies, then add the users accordingly. The admin account has to do this even for their own access.


## Misc & FAQ
### "Insufficient Permissions" when logging in to NiFi
This means that the account exists, but has not been configured for any permissions within NiFi. Refer to the [NiFi details section for the steps required](#adding-permissions-for-users-to-login).

### I can't create any processes, even ass the admin
This means that you have not yet added certain policies for the user. Note that this is required even for the administrator account, who by default does not have these permissions. Refer to the [NiFi details section for the steps required.](#giving-users-permissions-to-view-nifi-processes)

### How to configure local NiFi
We will need to update the following files for NiFi if done locally:

- ./conf/nifi.properties
- ./conf/login-identity-providers.xml

[Here is the official documentation](https://nifi.apache.org/docs/nifi-docs/html/administration-guide.html#ldap_login_identity_provider), or if preferred, [a reference link that you may use.](https://pierrevillard.com/2017/01/24/integration-of-nifi-with-ldap/)

#### nifi.properties
    nifi.login.identity.provider.configuration.file=./conf/login-identity-providers.xml
    nifi.security.user.login.identity.provider=ldap-provider

#### login-identity-providers.xml
    <provider>
        <identifier>ldap-provider</identifier>
        <class>org.apache.nifi.ldap.LdapProvider</class>
        <property name="Authentication Strategy">SIMPLE</property>
        <property name="Manager DN">cn=admin1,ou=people,dc=example,dc=org</property>
        <property name="Manager Password">password</property>
        <property name="TLS - Keystore"></property>
        <property name="TLS - Keystore Password"></property>
        <property name="TLS - Keystore Type"></property>
        <property name="TLS - Truststore"></property>
        <property name="TLS - Truststore Password"></property>
        <property name="TLS - Truststore Type"></property>
        <property name="TLS - Client Auth"></property>
        <property name="TLS - Protocol"></property>
        <property name="TLS - Shutdown Gracefully"></property>
        <property name="Referral Strategy">FOLLOW</property>
        <property name="Connect Timeout">10 secs</property>
        <property name="Read Timeout">10 secs</property>
        <property name="Url">ldap://openldap:1389</property>
        <property name="User Search Base">ou=people,dc=example,dc=org</property>
        <property name="User Search Filter">cn={0}</property>
        <property name="Identity Strategy">USE_DN</property>
        <property name="Authentication Expiration">12 hours</property>
    </provider>

Do change the above accordingly.

#### New keystore/truststore
You may refer to [the official documentation](https://nifi.apache.org/docs/nifi-docs/html/toolkit-guide.html), or you may also use [this link](https://pierrevillard.com/2016/11/29/apache-nifi-1-1-0-secured-cluster-setup/) for steps on how to use Nifi-Toolkit to produce them.