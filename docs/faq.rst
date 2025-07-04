.. _faq:

Frequently asked questions
==========================

Informational
-------------

Where to ask questions?
```````````````````````

First, please read this FAQ to check if your question is listed here.
Simple questions are best asked in our `Matrix`_ room.
For more complex questions, you can always open a `new discussion`_ on GitHub.


My installation is broken!
``````````````````````````

We are sorry to hear that. Please check for common mistakes and troubleshooting
advice in the `Technical issues`_ section of this page.

I think I found a bug!
``````````````````````

If you did not manage to solve the issue using this FAQ and there are not any
`open issues`_ describing the same problem, you can open a
`new issue`_ on GitHub.

I want a new feature or enhancement!
````````````````````````````````````

Great! We are always open for suggestions. We currently maintain two tags:

- ``type/enhancement``: Typically used for optimization of features in the project.
- ``type/feature``: For implementing new functionality,
  plugins and applications.

Feature requests are discussed on the discussion page of the project (see `feature requests`_).
Please check if your idea (or something similar) is already mentioned on the project.
If there is one open, you can choose to vote with a thumbs up, so we can
estimate the popular demand. Please refrain from writing comments like
*"me too"* as it clobbers the actual discussion.

If you can't find anything similar, you can open a `new feature request`_.
Please also share (where applicable):

- Use case: how does this improve the project?
- Any research done on the subject. Perhaps some links to upstream websites,
  reference implementations etc.

Why does my feature/bug take so long to solve?
``````````````````````````````````````````````

You should be aware that creating, maintaining and expanding a mail server
distribution requires a lot of effort. Mail servers are highly exposed to hacking attempts,
open relay scanners, spam and malware distributors etc. We need to work in a safe way and
have to prevent pushing out something quickly.

**TODO: Move the next section into the contributors part of docs**
We currently maintain a strict work flow:

#. Someone writes a solution and sends a pull request;
#. We use Github actions for some very basic building and testing;
#. The pull request needs to be code-reviewed and tested by at least two members
   from the contributors team.

Please consider that this project is mostly developed in people their free time.
We thank you for your understanding and patience.

I would like to donate (for a feature)
``````````````````````````````````````

We maintain a `Community Bridge`_ project through which you can donate.
This budget will be used to pay for development of features, mentorship and hopefully future events.
Contributing companies or individuals can be paid from this budget to support their development efforts.

We are also looking into GitHub's integrated sponsorship program for individual contributors.
Once those become available, we will add them to the project.

Please click the |sponsor| button on top of our GitHub Page for current possibilities.

.. |sponsor| image:: assets/sponsor-button.png
  :height: 1.2em
  :alt: sponsor
  :target: `GitHub`_


.. _`Matrix`: https://matrix.to/#/#mailu:tedomum.net
.. _`open issues`: https://github.com/Mailu/Mailu/issues
.. _`new issue`: https://github.com/Mailu/Mailu/issues/new
.. _`new discussion`: https://github.com/Mailu/Mailu/discussions/categories/user-support
.. _`feature requests`: https://github.com/Mailu/Mailu/discussions/categories/feature-requests-ideas
.. _`new feature request`: https://github.com/Mailu/Mailu/discussions/new?category=feature-requests-ideas
.. _`GitHub`: https://github.com/Mailu/Mailu
.. _`Community Bridge`: https://funding.communitybridge.org/projects/mailu

Deployment related
------------------

What is the difference between DOMAIN and HOSTNAMES?
````````````````````````````````````````````````````

Similar questions:

- Changing domain doesn't work
- Do I need a certificate for ``DOMAIN``?

``DOMAIN`` is the main mail domain. Aka, server identification for outgoing mail. DMARC reports point to ``POSTMASTER`` @ ``DOMAIN``.
These are really the only things it is used for. You don't need a cert for ``DOMAIN``, as it is a mail domain only and not used as host in any sense.
However, it is usual that ``DOMAIN`` gets setup as one of the many mail domains. None of the mail domains ever need a certificate.
TLS certificates work on host connection level only.

``HOSTNAMES`` however, can be used to connect to the server. All host names supplied in this variable will need a certificate. When ``TLS_FLAVOR=letsencrypt`` is set,
a certificate is requested automatically for all those domains.

So when you have something like this:

.. code-block:: bash

  DOMAIN=example.com
  POSTMASTER=me
  HOSTNAMES=mail.example.com,mail.foo.com,bar.com
  TLS_FLAVOR=letsencrypt

- You'll end up with a DMARC address to ``me@example.com``.
- Server identifies itself as the SMTP server of ``@example.com`` when sending mail. Make sure your reverse DNS hostname is part of that domain!
- Your server will have certificates for the 3 hostnames. You will need to create ``A`` and ``AAAA`` records for those names,
  pointing to the IP addresses of your server.
- The admin interface generates ``MX`` and ``SPF`` examples which point to the first entry of ``HOSTNAMES`` but these are only examples.
  You can modify them to use any other ``HOSTNAMES`` entry.

Your mail service will be reachable for IMAP, POP3, SMTP and Webmail at the addresses:

- mail.example.com
- mail.foo.com
- bar.com

.. note::

  In this case ``example.com`` is not reachable as a host and will not have a certificate.
  It can be used as a mail domain if MX is setup to point to one of the ``HOSTNAMES``. However, it is possible to include ``example.com`` in ``HOSTNAMES``.

*Issue reference:* `742`_, `747`_.

How to make IPv6 work?
``````````````````````

Docker IPv6 interfacing with ``ip6tables``, which is required for proper IPv6 support, is currently considered experimental.

Although the supposed way to enable IPv6 would be to give each container a publicly routable address, docker's IPv6 support
uses NAT to pass outside connections to the containers.

Currently we recommend to use `docker-ipv6nat` by `Robert Klarenbeek <https://github.com/robbertkl>` instead of docker's
experimental support.

Before enabling IPv6 you **MUST** disable the userland-proxy in your ``/etc/docker/daemon.json`` to not create an Open Relay!

.. code-block:: json

  {
      "userland-proxy": false
  }

You can enable `docker-ipv6nat` like this:

  docker run -d --name ipv6nat --privileged --network host --restart unless-stopped -v /var/run/docker.sock:/var/run/docker.sock:ro -v /lib/modules:/lib/modules:ro robbertkl/ipv6nat

If you want to try docker's experimental IPv6 support, it can be enabled like this:

.. code-block:: json

  {
      "userland-proxy": false,
      "ipv6": true,
      "experimental": true,
      "fixed-cidr-v6": "fd00:1234:abcd::/48",
      "ip6tables": true
  }

and enabling the IPv6 checkbox in the `setup utility`_.

This setup however is not officially supported, and might result in unforeseen issues.
With bad misconfiguration you might even cause your instance to become an Open Relay, you have been warned!

.. _`setup utility`: https://setup.mailu.io

How does Mailu scale up?
````````````````````````

Recent works allow Mailu to be deployed in Docker Kubernetes.
This means it can be scaled horizontally. For more information, refer to :ref:`kubernetes`.

*Issue reference:* `165`_, `520`_.

How to achieve HA / fail-over?
``````````````````````````````

The mailboxes and databases for Mailu are kept on the host filesystem under ``$ROOT/``.
For making the **storage** highly available, all sorts of techniques can be used:

- Local raid-1
- btrfs in raid configuration
- Distributed network filesystems such as GlusterFS or CEPH

Note that no storage HA solution can protect against accidental deletes or file corruptions.
Therefore it is advised to create backups on a regular base!

A backup MX can be configured as **failover**. For this you need a separate server running
Mailu. On that server, your domains will need to be setup as "Relayed domains", pointing
to you main server. MX records for the mail domains with a higher priority number will have
to point to this server. Please be aware that a backup MX can act as a `spam magnet`_ (archive.org).

For **service** HA, please see: `How does Mailu scale up?`_


*Issue reference:* `177`_, `591`_.

.. _`spam magnet`: https://web.archive.org/web/20130131032707/https://blog.zensoftware.co.uk/2012/07/02/why-we-tend-to-recommend-not-having-a-secondary-mx-these-days/

Does Mailu run on Rancher?
``````````````````````````

There is a rancher catalog for Mailu in the `Mailu/Rancher`_ repository. The user group for Rancher is small,
so we cannot promise any support on this when you are heading into trouble. See the repository README for more details.

*Issue reference:* `125`_.

.. _`Mailu/Rancher`: https://github.com/Mailu/Rancher


Can I run Mailu without host iptables?
``````````````````````````````````````

When disabling iptables in docker, its forwarding proxy process takes over.
This creates the situation that every incoming connection on port 25 seems to come from the
local network (docker's 172.17.x.x) and is accepted. This causes an open relay!

For that reason we do **not** support deployment on Docker hosts without iptables.

*Issue reference:* `332`_.

.. _override-label:

How can I override settings?
````````````````````````````

Postfix, Dovecot, Nginx and Rspamd support overriding configuration files. Override files belong in
``$ROOT/overrides``. Please refer to the official documentation of those programs for the
correct syntax. The following file names will be taken as override configuration:

- `Postfix`_ :
   - ``main.cf`` as ``$ROOT/overrides/postfix/postfix.cf``
   - ``master.cf`` as ``$ROOT/overrides/postfix/postfix.master``
   - All ``$ROOT/overrides/postfix/*.map`` files
   - For both ``postfix.cf`` and ``postfix.master``, you need to put one configuration per line, as they are fed line-by-line
     to postfix.
   - ``logrotate.conf`` as ``$ROOT/overrides/postfix/logrotate.conf`` - Replaces the logrotate.conf file used for rotating ``POSTFIX_LOG_FILE``.
- `Dovecot`_ - ``dovecot.conf`` in dovecot sub-directory.
- `Nginx`_ :
   - All ``*.conf`` files in the ``nginx`` sub-directory.
   - ``proxy.conf`` in the ``nginx/dovecot`` sub-directory.
- `Rspamd`_ - All files in the ``rspamd`` sub-directory.
- `Roundcube`_ - All ``*.inc.php`` files in the ``roundcube`` sub directory.

To override the root location (``/``) in Nginx ``WEBROOT_REDIRECT`` needs to be set to ``none`` in the env file (see :ref:`web settings <web_settings>`).

*Issue reference:* `206`_, `1368`_.

I want to integrate Nextcloud 15 (and newer) with Mailu
```````````````````````````````````````````````````````

1. Enable External user support from Nextcloud Apps interface

2. Configure additional user backends in Nextcloud’s configuration config/config.php using the following syntax if you use at least Nextcloud 15.

.. code-block:: bash

  <?php

  /** Use this for Nextcloud 15 and newer **/
  'user_backends' => array(
      array(
          'class' => 'OC_User_IMAP',
          'arguments' => array(
            '127.0.0.1', 993, 'ssl', 'example.com', true, false
        ),
      ),
  ),


If a domain name (e.g. example.com) is specified, then this makes sure that only users from this domain will be allowed to login.
After successful login the domain part will be stripped and the rest used as username in Nextcloud. e.g. 'username@example.com' will be 'username' in Nextcloud. Disable this behaviour by changing true (the fifth parameter) to false.

*Issue reference:* `575`_.

I want to integrate Nextcloud 14 (and older) with Mailu
```````````````````````````````````````````````````````

1. Install dependencies required to authenticate users via imap in Nextcloud

.. code-block:: bash

  apt-get update \
   && apt-get install -y libc-client-dev libkrb5-dev \
   && rm -rf /var/lib/apt/lists/* \
   && docker-php-ext-configure imap --with-kerberos --with-imap-ssl \
   && docker-php-ext-install imap

2. Enable External user support from Nextcloud Apps interface

3. Configure additional user backends in Nextcloud’s configuration config/config.php using the following syntax for Nextcloud 14 (and below):

.. code-block:: bash

  <?php

  /** Use this for Nextcloud 14 and older **/
  'user_backends' => array(
      array(
          'class' => 'OC_User_IMAP',
          'arguments' => array(
              '{imap.example.com:993/imap/ssl}', 'example.com'
          ),
      ),
  ),

If a domain name (e.g. example.com) is specified, then this makes sure that only users from this domain will be allowed to login.
After successfull login the domain part will be striped and the rest used as username in Nextcloud. e.g. 'username@example.com' will be 'username' in Nextcloud.

*Issue reference:* `575`_.


How do I use webdav (radicale)?
```````````````````````````````

| For first time set up, the user must access radicale via the url `https://mail.example.com/webdav/.web` and then
| 1. Log in using the  user's full email address and password.
| 2. Click 'Create new addressbook or calendar'
| 3. Follow instructions for creating an addressbook (for contact management) and calendar.
|
| Subsequently to use webdav (radicale), you can configure your carddav/caldav client to use the following url:
| `https://mail.example.com/webdav/user@example.com`
| As username you must provide the complete email address (user@example.com).
| As password you must provide the password of the email address.
| The user must be an existing Mailu user.

*issue reference:* `1591`_.


.. _`Postfix`:   http://www.postfix.org/postconf.5.html
.. _`Dovecot`:   https://doc.dovecot.org/configuration_manual/config_file/config_file_syntax/
.. _`NGINX`:     https://nginx.org/en/docs/
.. _`Rspamd`:    https://www.rspamd.com/doc/configuration/index.html
.. _`Roundcube`: https://github.com/roundcube/roundcubemail/wiki/Configuration#customize-the-look

.. _`125`: https://github.com/Mailu/Mailu/issues/125
.. _`165`: https://github.com/Mailu/Mailu/issues/165
.. _`177`: https://github.com/Mailu/Mailu/issues/177
.. _`332`: https://github.com/Mailu/Mailu/issues/332
.. _`742`: https://github.com/Mailu/Mailu/issues/742
.. _`747`: https://github.com/Mailu/Mailu/issues/747
.. _`520`: https://github.com/Mailu/Mailu/issues/520
.. _`591`: https://github.com/Mailu/Mailu/issues/591
.. _`575`: https://github.com/Mailu/Mailu/issues/575
.. _`1591`: https://github.com/Mailu/Mailu/issues/1591

.. _mta-sts:

How do I setup a MTA-STS policy?
````````````````````````````````

Mailu can serve an `MTA-STS policy`_; To configure it you will need to:

1. add ``mta-sts.example.com`` to the ``HOSTNAMES`` configuration variable (and ensure that a valid SSL certificate is available for it; this may mean restarting your smtp container)

2. configure an override with the policy itself; for example, your ``overrides/nginx/mta-sts.conf`` could read:

.. code-block:: bash

   location ^~ /.well-known/mta-sts.txt {
   return 200 "version: STSv1
   mode: enforce
   max_age: 1296000
   mx: mailu.example.com\r\n";
   }

3. setup the appropriate DNS/CNAME record (``mta-sts.example.com`` -> ``mailu.example.com``) and DNS/TXT record (``_mta-sts.example.com`` -> ``v=STSv1; id=1``) paying attention to the ``TTL`` as this is used by MTA-STS.

*issue reference:* `1798`_.

.. _`1798`: https://github.com/Mailu/Mailu/issues/1798
.. _`MTA-STS policy`: https://datatracker.ietf.org/doc/html/rfc8461

Technical issues
----------------

In this section we are trying to cover the most common problems our users are having.
If your issue is not listed here, please consult issues with the `troubleshooting tag`_.

.. _delete_users:

How to delete users?
````````````````````

From the web administration interface, when a user is deleted, the user is only disabled. When a user is not enabled, this user:

* cannot send/receive email
* cannot access Mailu (admin/webmail)
* cannot access the email box via pop3/imap

It is not possible to delete users via the Mailu web administration interface. The main reason is to prevent email address reuse. If a user was deleted, it can be recreated and used by someone else. It is not clear that the email address has been used by someone else previously. This new user might receive emails which were meant for the previous user. Disabling the user, prevents the email address to be reused by mistake.

Another reason is that extra post-deletion steps are required after a user has been deleted from the Mailu database. Those additional steps are:

* Delete the dovecot mailbox. If this does not happen, a new user with the same email address reuses the previous user's mailbox.
* Delete the user from the roundcube database (not required when SnappyMail is used). If this does not happen, a new user with the same email address reuses the previous roundcube data (such as address lists, gpg keys etc).

For safely deleting the user data (and possible the user as well) a script has been introduced. The scripts provides the following information

* commands for deleting mailboxes of unknown users. These users were deleted from Mailu, but still have their mailbox data on the file system.
* commands for deleting mailboxes and roundcube data for disabled users.
* commands for deleting users from the Mailu database.

Proceed as following for deleting an user:

1. Disable the to-be-deleted user. This can be done via the Web Administration interface (/admin), the Mailu CLI command user-delete, or the RESTful API. Do **not** delete the user.
2. Download .\\scripts\\purge_user.sh from the `github project`_. Or clone the Mailu github project.
3. Copy the script purge_user.sh to the Mailu folder that contains the `docker-compose.yml` file.
4. Run as root: purge_user.sh
5. The script will output the commands that can be used for fully purging each disabled user. It will show the instruction for deleting the user from the

   * Dovecot maildir from filesystem (all email data)
   * Roundcube database (all data saved in roundcube)
   * Mailu database.

6. Run the commands for deleting all user data for each disabled user.

.. _`github project`: https://github.com/Mailu/Mailu/


How to unblock an IP from rate limiter manually?
````````````````````````````````````````````````

To manually unblock an IP from the rate limiter do the following on your CLI:

.. code-block:: bash

  # list the limited networks (this is not the IP, but only the network part according to AUTH_RATELIMIT_IP_V4_MASK
  $ docker compose exec redis redis-cli -n 2 --scan --pattern 'LIMITER/auth-ip/*'

  # remove from rate limiter
  $ IP=8.8.8.8; docker compose exec redis redis-cli -n 2 --scan --pattern "LIMITER/auth-ip/${IP}/*" \
  | xargs -r docker compose exec -T redis redis-cli -n 2 DEL

Consider using :ref:`AUTH tokens` for your users. Token-based authentication is exempted from rate limits!

Also have a look at the configuration parameters
``AUTH_RATELIMIT_EXEMPTION`` and ``AUTH_REQUIRE_TOKENS``. More on
:ref:`Rate limiting<AUTH Ratelimit>` and :ref:`advanced settings<advanced_settings>`.

*Issue reference:* `2856`_.

.. _`2856`: https://github.com/Mailu/Mailu/issues/2856

Changes in .env don't propagate
```````````````````````````````

Variables are sent to the containers at creation time. This means you need to take the project
down and up again. A container restart is not sufficient.

.. code-block:: bash

  docker compose down && \
  docker compose up -d

*Issue reference:* `615`_.

SMTP Banner from overrides/postfix.cf is ignored
````````````````````````````````````````````````

Any mail related connection is proxied by the front container. Therefore the SMTP Banner is also set by front container. Overwriting in overrides/postfix.cf does not apply.

*Issue reference:* `1368`_.

.. _`1368`: https://github.com/Mailu/Mailu/issues/1368

My emails are getting rejected, I am being told to slow down, what can I do?
````````````````````````````````````````````````````````````````````````````

Some email operators insist that emails are delivered slowly. Mailu maintains two separate queues for such destinations: ``polite`` and ``turtle``. To enable them for some destination you can creating an override at ``overrides/postfix/transport.map`` as follow:

.. code-block:: bash

   yahoo.com   polite:
   orange.fr   turtle:

Re-starting the smtp container will be required for changes to take effect.

*Issue reference:* `2213`_.

.. _`2213`: https://github.com/Mailu/Mailu/issues/2213

My emails are getting deferred, what can I do?
``````````````````````````````````````````````

Emails are asynchronous and it's not abnormal for them to be defered sometimes. That being said, Mailu enforces secure connections where possible using DANE and MTA-STS, both of which have the potential to delay indefinitely delivery if something is misconfigured.

If delivery to a specific domain fails because their DANE records are invalid or their TLS configuration inadequate (expired certificate, ...), you can assist delivery by downgrading the security level for that domain by creating an override at ``overrides/postfix/tls_policy.map`` as follow:

.. code-block:: bash

   domain.example.com   may
   domain.example.org   encrypt

The syntax and options are as described in `postfix's documentation`_. Re-starting the smtp container will be required for changes to take effect.

.. _`postfix's documentation`: http://www.postfix.org/postconf.5.html#smtp_tls_policy_maps

403 - Access Denied Errors
``````````````````````````

While this may be due to several issues, check to make sure your ``DOMAIN=`` entry is the **first** entry in your ``HOSTNAMES=``.

TLS certificate issues
``````````````````````

When there are issues with the TLS/SSL certificates, Mailu denies service on secure ports.
This is a security precaution. Symptoms are:

- 403 browser errors;

These issues are typically caused by four scenarios:

#. ``TLS_FLAVOR=notls`` in ``.env``;
#. Certificates expired;
#. When ``TLS_FLAVOR=letsencrypt``, it might be that the *certbot* script is not capable of
   obtaining the certificates for your domain. See `letsencrypt issues`_
#. When ``TLS_FLAVOR=cert``, certificates are supposed to be copied to ``/mailu/certs``.
   Using an external ``letsencrypt`` program, it tends to happen when people copy the whole
   ``letsencrypt/live`` directory containing symlinks. Symlinks do not resolve inside the
   container and therefore it breaks the TLS implementation.

letsencrypt issues
..................

In order to determine the exact problem on TLS / Let's encrypt issues, it might be helpful
to check the logs.

.. code-block:: bash

  docker compose logs front | less -R
  docker compose exec front less /var/log/letsencrypt/letsencrypt.log

Common problems:

- Port 80 not reachable from outside.
- Faulty DNS records: make sure that all ``HOSTNAMES`` have **A** (IPv4) and **AAAA** (IPv6)
  records, pointing the the ``BIND_ADDRESS4`` and ``BIND_ADDRESS6``.
- DNS cache not yet expired. It might be that old / faulty DNS records are stuck in a cache
  en-route to letsencrypt's server. The time this takes is set by the ``TTL`` field in the
  records. You'll have to wait at least this time after changing the DNS entries.
  Don't keep trying, as you might hit `rate-limits`_.

.. _`rate-limits`: https://letsencrypt.org/docs/rate-limits/

Copying certificates
....................

As mentioned above, care must be taken not to copy symlinks to the ``/mailu/certs`` location.

**The wrong way!:**

.. code-block:: bash

  cp -r /etc/letsencrypt/live/domain.com /mailu/certs

**The right way!:**

.. code-block:: bash

  mkdir -p /mailu/certs
  cp /etc/letsencrypt/live/domain.com/privkey.pem /mailu/certs/key.pem
  cp /etc/letsencrypt/live/domain.com/fullchain.pem /mailu/certs/cert.pem

See also :ref:`external_certs`.

*Issue reference:* `426`_, `615`_.

How do I activate DKIM and DMARC?
`````````````````````````````````
Go into the Domain Panel and choose the Domain you want to enable DKIM for.
Click the first icon on the left side (domain details).
Now click on the top right on the *"Regenerate Keys"* Button.
This will generate the DKIM and DMARC entries for you.

*Issue reference:* `102`_.

.. _Fail2Ban:

Do you support Fail2Ban?
````````````````````````

Fail2Ban is not included in Mailu. Fail2Ban needs to modify the host's IP tables in order to
ban the addresses. We consider such a program should be run on the host system and not
inside a container. The ``front`` container does use authentication rate limiting to slow
down brute force attacks. The same applies to login attempts via the single sign on page.

We *do* provide a possibility to export the logs from the ``front`` service and ``Admin`` service to the host.
The ``front`` container logs failed logon attempts on SMTP, IMAP and POP3.
The ``Admin`` container logs failed logon attempt on the single sign on page.
You will need to setup the proper Regex in the Fail2Ban configuration.
Below an example how to do so.

If you use a reverse proxy in front of Mailu, it is vital to set the environment variables REAL_IP_HEADER and REAL_IP_FROM.
Without these environment variables, Mailu will not trust the remote client IP passed on by the reverse proxy and as a result your reverse proxy will be banned.

See the :ref:`configuration reference <reverse_proxy_headers>` for more information.


Assuming you have a working Fail2Ban installation on the host running your Docker containers,
follow these steps:

1. In the mailu docker compose set the logging driver of the front container to journald; and set the tag to mailu-front

.. code-block:: bash

  logging:
    driver: journald
    options:
      tag: mailu-front

2. Add the /etc/fail2ban/filter.d/bad-auth-bots.conf

.. code-block:: bash

  # Fail2Ban configuration file
  [Definition]
  failregex = ^\s?\S+ mailu\-front\[\d+\]: \S+ \S+ \[info\] \d+#\d+: \*\d+ client login failed: \"AUTH not supported\" while in http auth state, client: <HOST>, server:
  ignoreregex =
  journalmatch = CONTAINER_TAG=mailu-front

3. Add the /etc/fail2ban/jail.d/bad-auth-bots.conf

.. code-block:: bash

  [bad-auth-bots]
  enabled = true
  backend = systemd
  filter = bad-auth-bots
  bantime = 604800
  findtime = 600
  maxretry = 5
  action = docker-action-net

The above will block flagged IPs for a week, you can of course change it to your needs.

4.  Add the following to /etc/fail2ban/action.d/docker-action-net.conf

IMPORTANT: You have to install ipset on the host system, eg. `apt-get install ipset` on a Debian/Ubuntu system.

See ipset homepage for details on ipset, https://ipset.netfilter.org/.

.. code-block:: bash

  [Definition]

  actionstart = ipset --create f2b-bad-auth-bots nethash
                iptables -I DOCKER-USER -m set --match-set f2b-bad-auth-bots src -p tcp -m tcp --dport 25 -j DROP

  actionstop = iptables -D DOCKER-USER -m set --match-set f2b-bad-auth-bots src -p tcp -m tcp --dport 25 -j DROP
               ipset --destroy f2b-bad-auth-bots


  actionban = ipset add -exist f2b-bad-auth-bots <ip>/24

  actionunban = ipset del -exist f2b-bad-auth-bots <ip>/24

Using DOCKER-USER chain ensures that the blocked IPs are processed in the correct order with Docker. See more in: https://docs.docker.com/network/iptables/.

Please note that the provided example will block the subnet from sending any email to the Mailu instance.

5. In the mailu docker-compose set the logging driver of the Admin container to journald; and set the tag to mailu-admin

.. code-block:: bash

  logging:
    driver: journald
    options:
      tag: mailu-admin

6. Add the /etc/fail2ban/filter.d/bad-auth.conf

.. code-block:: bash

  # Fail2Ban configuration file
  [Definition]
  failregex = : Authentication attempt from <HOST>(?: for (?:[^ ]+@[^ ]+))? has been rate-limited\.$
  ignoreregex =
  journalmatch = CONTAINER_TAG=mailu-admin

7. Add the /etc/fail2ban/jail.d/bad-auth.conf

.. code-block:: bash

  [bad-auth]
  enabled = true
  backend = systemd
  filter = bad-auth
  bantime = 604800
  findtime = 900
  maxretry = 15
  action = docker-action

The above will block flagged IPs for a week, you can of course change it to your needs.

8.  Add the following to /etc/fail2ban/action.d/docker-action.conf

.. code-block:: bash

  [Definition]

  actionstart = ipset --create f2b-bad-auth iphash
                iptables -I DOCKER-USER -m set --match-set f2b-bad-auth src -j DROP

  actionstop = iptables -D DOCKER-USER -m set --match-set f2b-bad-auth src -j DROP
               ipset --destroy f2b-bad-auth


  actionban = ipset add -exist f2b-bad-auth <ip>

  actionunban = ipset del -exist f2b-bad-auth <ip>

Using DOCKER-USER chain ensures that the blocked IPs are processed in the correct order with Docker. See more in: https://docs.docker.com/network/iptables/

9. Configure and restart the Fail2Ban service

Make sure Fail2Ban is started after the Docker service by adding a partial override which appends this to the existing configuration.

.. code-block:: bash

  sudo systemctl edit fail2ban

Add the override and save the file.

.. code-block:: bash

  [Unit]
  After=docker.service

Restart the Fail2Ban service.

.. code-block:: bash

  sudo systemctl restart fail2ban

*Issue reference:* `85`_, `116`_, `171`_, `584`_, `592`_, `1727`_.

Users can't change their password from webmail
``````````````````````````````````````````````

All users have the ability to login to the admin interface. Non-admin users
have only restricted functionality such as changing their password and the
spam filter weight settings.

*Issue reference:* `503`_.

rspamd: DNS query blocked on multi.uribl.com
````````````````````````````````````````````

This usually relates to the DNS server you are using. Most of the public servers block this query or there is a rate limit.
In order to solve this, you most probably are better off using a root DNS resolver, such as `unbound`_. This can be done in multiple ways:

- Use the *Mailu/unbound* container. This is an optional include when generating the ``docker-compose.yml`` file with the setup utility.
- Setup unbound on the host and make sure the host's ``/etc/resolve.conf`` points to local host.
  Docker will then forward all external DNS requests to the local server.
- Set up an external DNS server with root resolving capabilities.

In any case, using a dedicated DNS server will improve the performance of your mail server.

*Issue reference:* `206`_, `554`_, `681`_.

Can I learn ham/spam messages from an already existing mailbox?
```````````````````````````````````````````````````````````````
Mailu supports automatic spam learning for messages moved to the Junk mailbox. Any email moved from the Junk Folder will learnt as ham.

If you already have an existing mailbox and want Mailu to learn them all as ham messages, you might run rspamc from within the dovecot container:

.. code-block:: bash

  rspamc -h antispam:11334 -P mailu -f 13 fuzzy_add /mail/user\@example.com/.Ham_Learn/cur/
  rspamc -h antispam:11334 -P mailu learn_ham /mail/user\@example.com/.Ham_Learn/cur/

This should learn every file located in the ``Ham_Learn`` folder from user@example.com

Likewise, to lean all messages within the folder ``Spam_Learn`` as spam messages :

.. code-block:: bash

  rspamc -h antispam:11334 -P mailu -f 11 fuzzy_add /mail/user\@example.com/.Spam_Learn/cur/
  rspamc -h antispam:11334 -P mailu learn_spam /mail/user\@example.com/.Spam_Learn/cur/

*Issue reference:* `1438`_.

Is there a way to support more (older) ciphers?
```````````````````````````````````````````````

You will need to rewrite the `tls.conf` template of the `front` container in `core/nginx`.

You can set the protocols as follow:

.. code-block:: bash

  ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
  ssl_ciphers <list of ciphers>;

After applying the change, you will need to rebuild the image and use it in your deployment.

We **strongly** advice against downgrading the TLS version and ciphers, please upgrade your client instead! We will not support a more standard way of setting this up.

*Issue reference:* `363`_, `698`_.

Why does Compose complain about the yaml syntax
```````````````````````````````````````````````

In many cases, Docker Compose will complain about the yaml syntax because it is too old. It is especially true if you installed Docker Compose as part of your GNU/Linux distribution package system.

Unless your distribution has proper up-to-date packages for Compose, we strongly advise that you install it either:

 - from the Docker-CE repositories along with Docker CE itself,
 - from PyPI using `pip install docker compose` or
 - from Github by downloading it directly.

Detailed instructions can be found at https://docs.docker.com/compose/install/

*Issue reference:* `853`_.

Why are spam mails being discarded?
`````````````````````````````````````````

Disabling antispam in the user settings actually disables automatic classification of messages as spam and stops moving them to the `junk` folder. It does not stop spam scanning and filtering.

Therefore, messages still get discarded if their spam score is so high that the antispam finds them unfit for distribution. Also, the antispam headers are still present in the message, so that mail clients can display it and classify based on it.

*Issue reference:* `897`_.

Why is SPF failing while properly setup?
````````````````````````````````````````

Very often, SPF failure is related to Mailu sending emails with a different IP address than the one configured in the env file.

This is mostly due to using a separate IP address for Mailu and still having masquerading NAT setup for Docker, which results in a different outbound IP address. You can simply check the email headers on the receiving side to confirm this.

If you wish to explicitly NAT Mailu outbound traffic, it is usually easy to source-NAT outgoing SMTP traffic using iptables :

```
iptables -t nat -A POSTROUTING -o eth0 -p tcp --dport 25 -j SNAT --to <your mx ip>
```

*Issue reference:* `1090`_.


.. _`troubleshooting tag`: https://github.com/Mailu/Mailu/issues?utf8=%E2%9C%93&q=label%3Afaq%2Ftroubleshooting
.. _`85`: https://github.com/Mailu/Mailu/issues/85
.. _`102`: https://github.com/Mailu/Mailu/issues/102
.. _`116`: https://github.com/Mailu/Mailu/issues/116
.. _`171`: https://github.com/Mailu/Mailu/issues/171
.. _`206`: https://github.com/Mailu/Mailu/issues/206
.. _`363`: https://github.com/Mailu/Mailu/issues/363
.. _`426`: https://github.com/Mailu/Mailu/issues/426
.. _`503`: https://github.com/Mailu/Mailu/issues/503
.. _`554`: https://github.com/Mailu/Mailu/issues/554
.. _`584`: https://github.com/Mailu/Mailu/issues/584
.. _`592`: https://github.com/Mailu/Mailu/issues/592
.. _`615`: https://github.com/Mailu/Mailu/issues/615
.. _`681`: https://github.com/Mailu/Mailu/pull/681
.. _`698`: https://github.com/Mailu/Mailu/issues/698
.. _`853`: https://github.com/Mailu/Mailu/issues/853
.. _`897`: https://github.com/Mailu/Mailu/issues/897
.. _`1090`: https://github.com/Mailu/Mailu/issues/1090
.. _`unbound`: https://nlnetlabs.nl/projects/unbound/about/
.. _`1438`: https://github.com/Mailu/Mailu/issues/1438
.. _`1727`: https://github.com/Mailu/Mailu/issues/1727

A user gets ``Sender address rejected: Access denied. Please check the`` ``message recipient […] and try again`` even though the sender is legitimate?
``````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````````

First, check if you are really sure the user is a legitimate sender, i.e. the registered user is authenticated successfully and own either the account or alias he/she is trying to send from. If you are really sure this is correct, then the user might try to erroneously send via port 25 instead of the designated SMTP client-ports. Port 25 is meant for server-to-server delivery, while users should use port 587 or 465.

The admin container won't start and its log says ``Critical: your DNS resolver isn't doing DNSSEC validation``
``````````````````````````````````````````````````````````````````````````````````````````````````````````````
Since v1.9, Mailu requires a **validating** DNSSEC enabled DNS resolver. To check whether your DNS resolver (and its upstream) fits the requirements you can use the following command and see whether the **AD** flag is present in the reply:

.. code-block:: bash

  dig @<ip> +adflag example.org A

We recommend that you run your own DNS resolver (enable unbound and update your docker-compose.yml when you update from older versions) instead of relying on publicly available ones. It's better security-wise (you don't have to trust them) and RBLs used by rspamd are known to rate-limit per source-ip address.

We have seen a fair amount of support requests related to the following:

- dnsmasq won't forward DNSSEC results unless instructed to do so. If you are running openwrt or pi-hole, you do need to enable DNSSEC.
- systemd-resolve won't validate DNSSEC results unless instructed to do so. If you are using it you can check its configuration using ``systemd-resolve --status | grep DNSSEC``
- `coredns has a bug`_ that we have now worked around
- `netplan does not play nicely with docker` by default and may need to be configured to leave docker's network alone.

.. _`coredns has a bug`: https://github.com/coredns/coredns/issues/5189

.. _`netplan does not play nicely with docker`: https://github.com/Mailu/Mailu/issues/2868#issuecomment-1606014184

How can I use Mailu without docker?
```````````````````````````````````

Running Mailu without docker is not supported. If you want to do so, you need to export an environment variable called ``I_KNOW_MY_SETUP_DOESNT_FIT_REQUIREMENTS_AND_WONT_FILE_ISSUES_WITHOUT_PATCHES`` to the ``admin`` container.

We welcome patches but do not have the bandwidth to test and fix issues related to your unsupported setup. If you do want to help, we welcome new maintainers: please get in touch.

How can I add more languages to roundcube's spellchecker?
`````````````````````````````````````````````````````````

If you are comfortable using an online spellchecker, the easiest is to configure the following via an override:

.. code-block:: php

   $config['spellcheck_engine'] = 'googie';
   $config['spellcheck_ignore_caps'] = true;
   $config['spellcheck_ignore_nums'] = true;
   $config['spellcheck_dictionary'] = true;

If not, you can download the `aspell dictionary`_ you require and place it in ``/usr/share/aspell/`` and then enable it by tweaking the following in the configuration file:

.. code-block:: php

   $config['spellcheck_languages'] = array('en'=>'English', ...);

.. _`aspell dictionary`: http://ftp.gnu.org/gnu/aspell/dict/0index.html


I see a lot of "mount: Deactivated successfully." messages in the logs
``````````````````````````````````````````````````````````````````````

This is a docker & systemd issue: see `this workaround`_

.. _`this workaround`: https://stackoverflow.com/questions/63622619/docker-flooding-syslog-with-run-docker-runtime-logs/69415949#69415949


I see a lot of "Unable to lookup the TLSA record for XXX. Is the DNSSEC zone okay on ..." messages in the logs
``````````````````````````````````````````````````````````````````````````````````````````````````````````````

There may be multiple causes for it but if you are running docker 24.0.0, odds are you are `experiencing this docker bug`_ and the workaround is to switch to a different version of docker.

.. _`experiencing this docker bug`: https://github.com/Mailu/Mailu/issues/2827

How can I view and export the logs of a Mailu container?
````````````````````````````````````````````````````````

In some situations, a separate log is required. For example a separate mail log (from postfix) could be required due to legal reasons.

All Mailu containers log the output to journald. The logs are written to journald with the tag:

| mailu-<service name>
| where <service-name> is the name of the service in the docker-compose.yml file.
| For example, the service running postfix is called smtp. To view the postfix logs use:

.. code-block:: bash

  journalctl -t mailu-smtp

Note: ``SHIFT+G`` can be used to jump to the end of the log file. ``G`` can be used to jump back to the top of the log file.

To export the log files from journald to the file system, the logs could be imported into a syslog program like ``rsyslog``.
Via ``rsyslog`` the container specific logs could be written to a separate file using a filter.

Below are the steps for writing the postfix (mail) logs to a log file on the file system.

1. Install the ``rsyslog`` package. Note: on most distributions this program is already installed.
2. Edit ``/etc/systemd/journald.conf``.
3. Enable ``ForwardToSyslog=yes``. Note: on most distributions this is already enabled by default. This forwards journald to syslog.
4. ``sudo touch /var/log/postfix.log``. This step creates the mail log file.
5. ``sudo chown syslog:syslog /var/log/postfix.log``. This provides rsyslog the permissions for accessing this file.
6. Create a new config file in ``/etc/rsyslog.d/export-postfix.conf``
7. Add ``:programname, contains, "mailu-smtp" /var/log/postfix.log``. This instructs rsyslog to write the logs for mailu-smtp to a log file on file system.
8. ``sudo systemctl restart systemd-journald.service``
9. ``sudo systemctl restart rsyslog``
10. All messages from the smtp/postfix container are now logged to ``/var/log/postfix.log``.
11. Rsyslog does not perform log rotation. The program (package) ``log rotate`` can be used for this task. Install the ``logrotate`` package.
12. Modify the existing configuration file for rsyslog: ``sudo nano /etc/logrotate.d/rsyslog``
13. Add at the top add: ``/var/log/postfix.log``. Of course you can also use your own configuration. This is just an example. A complete example for configuring log rotate is:

.. code-block:: bash

  /var/log/postfix.log
  {
       rotate 4
       weekly
       missingok
       notifempty
       compress
       delaycompress
       sharedscripts
       postrotate
           /usr/lib/rsyslog/rsyslog-rotate
       endscript
  }

.. code-block:: bash

  #!/bin/sh
  #/usr/lib/rsyslog/rsyslog-rotate

  if [ -d /run/systemd/system ]; then
      systemctl kill -s HUP rsyslog.service
  fi


Admin container fails to connect to external MariaDB database
`````````````````````````````````````````````````````````````

If the admin container is `unable to connect to an external MariaDB database due to incompatible collation`_, you may need to change the ``SQLALCHEMY_DATABASE_URI`` setting to ensure the right connector is used.
Alternatively, you may set ``DB_APPENDIX`` accordingly. For example: ``?collation=utf8mb4_unicode_ci`` is appended as is just after the database name in case DB_TYPE and related values are set.

MariaDB has no support for utf8mb4_0900_ai_ci which is the new default since MySQL version 8.0.

.. _`unable to connect to an external MariaDB database due to incompatible collation`: https://github.com/Mailu/Mailu/issues/3449

Why is Rspamd giving me an "Illegal instruction" error ?
`````````````````````````````````````````````````````````

On Linux amd64 (x84_64), if the antispam container is crashing and gives you an ``Illegal instruction`` error, you may have a CPU that lacks support of the ``SSE4.2`` instruction set.
The more modern and FOSS ``vectorscan`` library used by rspamd superseeded the now closed source Intel ``hyperscan`` library in Alpine Linux, and since August 2024 it requires the ``SSE4.2`` instruction set to work properly.

Pre-2013 Intel Atom CPUs (Like N2800 or D425), Intel pre-Nehalem architectures and AMD pre-Bulldozer architectures do not support ``SSE4.2``.
To check if your CPU supports ``SSE4.2`` you can use this one liner command:

``if grep -q sse4_2 /proc/cpuinfo; then echo "CPU is SSE4.2 Capable"; else echo "CPU is NOT SSE4.2 capable"; fi``

A workaround to this issue is to use a x86_32 (or i686) version of rspamd, because the ``vectorscan`` library is only used on 64-bit capable systems.
Note that this may stop working in the future, as 32-bit software support is being progressively dropped.

*Issue reference:* `3713`_.

.. _`3713`: https://github.com/Mailu/Mailu/issues/3713
