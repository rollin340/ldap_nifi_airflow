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

### I can't create any processes, even ass the admin
Right-click on the Nifi canvas and select 'Manage Access Policies'. From here, you will have to create policies, then add the users accordingly. The admin account has to do this even for their own access.

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