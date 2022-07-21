# Local copy to test LDAP, NiFi, & Airflow

## Steps to run the project

### Setting up
- Run `setup_airflow_env.(sh/bat)` to create the `.env` file to ensure that files written by Airflow belongs to the host user. **Run this BEFORE you launch the containers.** You only need to re-run this part if you are running a fresh clone of this repository.
- Import the certificate `./nifi/nifi-cert.pem` to your browser. You can skip this step, but you will be required to click on the "Accept the risks and continue" button with every launch of NiFi.

### Set NiFi as a single instance, or as a cluster
By default, this project runs NiFi as a cluster of 5 containers. If you would like to run a single instance instead, edit the `docker-compose.yml` file, uncomment the `nifi` service, and comment out the `5 clustered nifi instances`, and the `nginx service`.

### Run the containers
On the Terminal from the project's root directory, run `docker compose up`.

### Enable 'memberOf' module in LDAP for Airflow
- To use Airflow, run `setup_ldap_memberof.sh`to enable LDAP to show "memberOf" details from each user. **This process recreates the initial LDAP tree, and should be done AFTER the container has started, but BEFORE new users/groups are created**

## Docker images used
- `bitnami/openldap`:`2`
- `ldapaccountmanager/lam`:`stable` AND/OR `osixia/phpldapadmin`:`latest`
- `bitnami/zookeeper`:`latest`
- `apache/nifi`:`latest`
- `postgres`:`13`
- `redis`:`latest`
- `apache/airflow`:`2.3.3`

## LDAP Details

### Org Tree
<pre>
─── dc=example,dc=org
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

### Default LDAP Passwords for initial setup

LDAP Administrator account is `cn=admin,dc=example,dc=org`, with the username `admin` and the password `adminpassword`.

All other users' passwords are set to `password`.

### Creating new groups

From the preferred LDAP manager, create a new child object under `ou=groups,dc=example,dc=org` of the `groupOfNames` object class.

Fill in the `cn` with the group's name, and add the members accordingly.

### Creating new accounts
From the preferred LDAP manager, create a new child object under `ou=people,dc=example,dc=org` of the `person` object class.

Fill in the `cn` and `sn` with the user's login ID, and fill in the `userPassword` attribute.


### Testing if user accounts exist
From any of a container within the project network, run the following:

    ldapsearch -H ldap://openldap:1389 -x -b 'ou=people,dc=example,dc=org' -D 'cn=admin,dc=example,dc=org' -w adminpassword

If successful, you should see the accounts above.

To view what groups each user is a member of, run the following:

    ldapsearch -H ldap://openldap:1389 -x -b 'ou=people,dc=example,dc=org' -D 'cn=admin,dc=example,dc=org' -w adminpassword memberOf    

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

### Cluster settings
By default, this repository uses a cluster of 5 nodes. If the number of nodes desired are to be updated, please ensure to do the following.

#### Reducing the amount of nodes

1. Comment out the unused nodes in the `docker-compose.yml` file.
2. Comment out the unused nodes in the `http/upstream` section in the `./nginx/nginx.conf`file.

#### Increasing the amount of nodes

1. Refer to this [section](#new-keystoretruststore) to create new keystore/truststore files for all nodes.
2. Copy the folders/files in the same manner of this project; `./nifi/cluster/nifi_X` where 'X' is the node number.
3. Update the `http/upstream` section in the `./nginx/nginx.conf`file to include the new nodes.
4. Update `,/nifi/cluster/authorizers.xml`:
    - Under the `userGroupProvider` section, add new `Initial User Identity` records as needed.
    - Under the `accessPolicyProvider` section, add new `Node Identity` records as needed.
5. Update the `docker-compose.yml` file by adding the new nodes with the appropriate `container_name`, `hostname`, and `volumes`.

## Airflow details

The default behavior of this configuration maps all users under the "admins" group with administrative perissions, and all users under "users" to the default Airflow "User" permissions.

Note that the default "User" permissions givess acces to **ALL** Dags.

### Adding new default profiles for users/groups to be mapped to
1. As an administrator, under the "security" tab, lick on "List Roles".
2. Click on the checkbox for "User", then hover over the "Actions" button and click on "Copy Role".
3. Edit the name, then delete "can read on DAGS", "can edit on DAGS", and "can delete on DAGS".
4. From the same field, type ":\<Tag to allow\>" to drill down the options, and add the permissions removed from step 3 but limited only to the tag.
5. Update the `AUTH_ROLES_MAPPING` section of `./airflow/webserver_config.py`, add make the desired changes.
    - 'cn=\<Group name\>,ou=groups,dc=example,dc=org': ['\<Role\>']
    - Multiple roles can be mapped as a comma delimited list

## Local configuration if not using Docker

Please note that this part may not be complete/accurate, and should be used with caution.

### How to configure a single local NiFi instance
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
You may refer to [the official documentation](https://nifi.apache.org/docs/nifi-docs/html/toolkit-guide.html#standalone), or you may also use [this link](https://pierrevillard.com/2016/11/29/apache-nifi-1-1-0-secured-cluster-setup/) for steps on how to use Nifi-Toolkit to produce them.

The following code was used for this project when NiFi is running a single instance:

    /opt/nifi/nifi-toolkit-current/bin/tls-toolkit.sh standalone --hostnames 'localhost' --clientCertDn 'CN=admin,OU=NiFi' --subjectAlternativeNames 'localhost,0.0.0.0,nifiserver1,nifiserver2,nifiserver3,nifiserver4,nifiserver5' --keyStorePassword ZZgvZrUBcGn3KE8C3Ny9xSRp3gSZM3hatYhCS83rFPk96Xcv2L --trustStorePassword wYpyy37LEbkxTeuhQ2WrvyWZAVpS2jwhj2EUCuAr24qr6DasR3 --outputDirectory /tmp/nifi_certs

The following code was used for this project when NiFi is running as a cluster of 5 nodes:

<pre><code>
/opt/nifi/nifi-toolkit-current/bin/tls-toolkit.sh standalone --hostnames 'nifi_<mark>[1-5]</mark>' --clientCertDn 'CN=admin,OU=NiFi' --subjectAlternativeNames 'localhost,0.0.0.0,nifiserver1,nifiserver2,nifiserver3,nifiserver4,nifiserver5' --keyStorePassword ZZgvZrUBcGn3KE8C3Ny9xSRp3gSZM3hatYhCS83rFPk96Xcv2L --trustStorePassword wYpyy37LEbkxTeuhQ2WrvyWZAVpS2jwhj2EUCuAr24qr6DasR3 --outputDirectory /tmp/nifi_certs
</code></pre>

Note that the `hostname` uses a pattern to automatically create the required files for 5 instances. Do change this part as desired.

### How to configure local LDAP to enable the 'memberOf' module
Firstly, run <code>ldapsearch -H ldapi:/// -Y EXTERNAL -b "cn=config" -LLL -Q "olcDatabase=*"</code> to find out the details of your HDB backend. Note that newer versions of OpenLDAP has moved to using MDB instead.

Create a new .ldif file. For this example, we will be naming it `memberof_config.ldif`. Change the following highlighted portions to match the directory of the LDAP libraries, and the appropriate {X} for the HDB backend.

`memberof_config.ldif`:
<pre><code>
    dn: cn=module{1},cn=config
    cn: module{1}
    objectClass: olcModuleList
    olcModuleLoad: memberof
    olcModulePath: <mark>/opt/bitnami/openldap/lib/openldap</mark>

    dn: olcOverlay={0}memberof,olcDatabase=<mark>{2}hdb</mark>,cn=config
    objectClass: olcConfig
    objectClass: olcMemberOf
    objectClass: olcOverlayConfig
    objectClass: top
    olcOverlay: memberof
    olcMemberOfDangling: ignore
    olcMemberOfRefInt: TRUE
    olcMemberOfGroupOC: groupOfNames
    olcMemberOfMemberAD: member
    olcMemberOfMemberOfAD: memberOf
</code></pre>

Once created, add the module with <code>sudo ldapadd -Q -Y EXTERNAL -H ldapi:/// -f ./memberof_config.ldif</code>.

Create another .ldif file to modify the entry. For this example, we will be naming it `refint1.ldif`. Check the loaded modules path to ensure that you are pointing to the corrent 'cn'. For example, in the bitnami/openldap image, they are found in `/bitnami/openldap/slapd.d/cn=config`.

`refint1.ldif`:
<pre><code>
    dn: cn=<mark>module{1}{0}</mark>,cn=config
    add: olcmoduleload
    olcmoduleload: refint
</code></pre>

Once created, modify the module with <code>sudo ldapmodify -Q -Y EXTERNAL -H ldapi:/// -f ./refint1.ldif</code>.

Create another .ldif file to modify the entry. For this example, we will be naming it `refint2.ldif`. Take note of the highlighted portion; if LDAP throws an error that 'manager' and/or 'owner'attribute types are undefined, remove them.

`refint2.ldif`:
<pre><code>
    dn: olcOverlay={1}refint,olcDatabase={2}hdb,cn=config
    objectClass: olcConfig
    objectClass: olcOverlayConfig
    objectClass: olcRefintConfig
    objectClass: top
    olcOverlay: {1}refint
    olcRefintAttribute: memberof member <mark>manager owner</mark>
</code></pre>

Once created, add the module with <code>ldapadd -Q -Y EXTERNAL -H ldapi:/// -f /tmp/refint2.ldif</code>.

From here, you can now add/modify/delete users/groups. Do note that a user must exist before being added to the group to enable the reverse mapping.

Reference: https://blog.adimian.com/2014/10/15/how-to-enable-memberof-using-openldap/

### How to configure Airflow
Do not create a local account if using LDAP for authentication, and ensure that the [LDAP 'memberOf' module is activated](#how-to-configure-local-ldap-to-enable-the-memberof-module).

Once that is done, you will have to update the `/opt/airflow/webserver_config.py` file. Do change the values as needed.

`webserver_config.py`:
<pre><code>
    import os
    from flask_appbuilder.security.manager import AUTH_LDAP

    AUTH_TYPE = AUTH_LDAP
    AUTH_LDAP_SERVER = '<mark>ldap://openldap:1389</mark>'
    AUTH_LDAP_USE_TLS = False

    AUTH_USER_REGISTRATION = True
    AUTH_USER_REGISTRATION_ROLE = "Public"
    AUTH_LDAP_FIRSTNAME_FIELD = "givenName"
    AUTH_LDAP_LASTNAME_FIELD = "sn"
    AUTH_LDAP_EMAIL_FIELD = "mail"

    AUTH_LDAP_SEARCH = '<mark>ou=people,dc=example,dc=org</mark>'
    AUTH_LDAP_UID_FIELD = "cn"

    AUTH_LDAP_BIND_USER = '<mark>cn=admin,dc=example,dc=org</mark>'
    AUTH_LDAP_BIND_PASSWORD = '<mark>adminpassword</mark>'

    AUTH_ROLES_MAPPING = {
        <mark>'cn=users,ou=groups,dc=example,dc=org': ['User'],
        'cn=admins,ou=groups,dc=example,dc=org': ['Admin'],</mark>
    }

    AUTH_LDAP_GROUP_FIELD = "memberOf"

    AUTH_ROLES_SYNC_AT_LOGIN = True
    PERMANENT_SESSION_LIFETIME = 1800
</code></pre>


Official documentation reference: https://airflow.apache.org/docs/apache-airflow/1.10.1/security.html?highlight=ldap#ldap

Alternate reference: https://www.notion.so/Airflow-with-LDAP-in-10-mins-cbcbe5690d3648f48ee7e8ca45cb755f

## Misc & FAQ
### "Insufficient Permissions" when logging in to NiFi
This means that the account exists, but has not been configured for any permissions within NiFi. Refer to the [NiFi details section for the steps required](#adding-permissions-for-users-to-login).

### I can't create any NiFi processes, even as the admin
This means that you have not yet added certain policies for the user. Note that this is required even for the administrator account, who by default does not have these permissions. Refer to the [NiFi details section for the steps required.](#giving-users-permissions-to-view-nifi-processes)

### Your user has no roles and/or permissions! when logging into Airflow
Airflow uses LDAP's 'memberOf' module to map permissions. Do ensure you have run the included script [as mentioned here](#enable-memberof-module-in-ldap-for-airflow), and try again.

### Firefox won't connect with the error "MOZILLA_PKIX_ERROR_CA_CERT_USED_AS_END_ENTITY"
From Firefox, go to Settings > Privacy & Security > View Certificates. On the 'Servers' tab, add 'https://localhost:8443'. Then on the 'Authorities' tab, import the certificate provided/created.

### The Flow Controller is initializing the Data Flow
Wait for approximately 1 minute for the NiFi cluster to be ready.