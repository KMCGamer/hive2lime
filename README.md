# hive2lime
Created by: Kyle Carhart

Table of contents
=================
1. Introduction
2. Lime Settings
3. Config files
4. End User Instructions 
5. Common Questions

Introduction
------------
In a nutshell, the hive2lime script takes cases from TheHive that have been marked as _Resolved_ and transfers some of the cases information to a LimeSurvey response. These responses can be accessed at a later date by the person who resolved the case.

Lime Settings
-------------
In order for this script to work, several options need to be enabled on LimeSurvey.

#### Global Settings

##### Enable API:

`Configuration > Global Settings > Interfaces`

- Set "RPC interface enabled" to __JSON-RPC__.

##### Create an API Admin Account:

`Configuration > Manage Survey Administrators`

1. Click Add User.
2. Fill out the username, email, and full name fields.
3. Click on the lock symbol to "set global permissions for this user."
4. __Enable__ "Permission to create surveys and view, update and delete surveys from other users."
5. __Enable__ "Use internal database authentication."
6. Click __Save__.

#### General Survey Settings

`Surveys > SURVEY_NAME > Survey Properties > General settings & texts`

- Set "Token-based response persistence" to __OFF__.
- Set "Allow multiple responses or update responses with one token" to __ON__.

Config Files
------------

All configuration options are here. If they are not here, then you will need to modifiy the script. The config files do not use quotes (""). When editing config files, make follow the examples below.

### hive.ini

Put all the information for TheHive into the hive.ini file. The URL should be the base url to access TheHive. The username and password are from the api user.

#### Example hive.ini:
```
[hive]
url = https://hive.com:9433
user = apiuser
password = pass
```

### lime.ini

All information for LimeSurvey should go into the lime.ini file. 

The `admin_panel` section is for the LimeSurvey API user credentials. 

The `misc` section is for the BASE URL to access limesurvey as well as the survey id for the active survey. 

The `mysql` section contains information to access limesurveys database for specific insertions. 

Tokens can be appended to the end of this file in the `tokens` section. Put the username of the person the token corresponds to from TheHive to LimeSurvey. To be clear, __the username is from TheHive and the token is from LimeSurvey__.

#### Example lime.ini:
```
[admin_panel]
user = apiuser
password = pass

[misc]
url = https://XXXXX/limesurvey/index.php
survey_id = 123456

[mysql]
user = mysqluser
password = pass
database = limesurvey

[tokens]
example = gIpPVHa699LgYm1
example2 = aI2kF7af4GL68mR
```

End User Instructions
---------------------

### Emails

Users that resolve cases on the hive should automatically get emails with instructions on how to access their LimeSurvey responses.

__In order for the user to recieve emails, their TheHive username must match the username of their mailbox.sc.edu email address!__

A user must do the following to complete their response:

1. Click on the link in the email (or navigate to the page where they can submit a response to the survey)
2. Enter your token into the field and click continue.
3. Click __Load unfinished survey__ in the navigation bar.
4. Type in a hive case number that has been resolved (these are listed in the email) into the __Saved Name field AND the Password field__. 
5. Complete the survey and submit it.

Common Questions
----------------

> I can't access my hive case id after I've submitted the limesurvey response for that case id.

Once you submit a survey repsonse, it gets removed from the mysql limesurvey saved response table which means you can no longer access it through the front-end. To make any changes to a response you've already submitted, you have to log in through the admin panel and edit it in the back-end.

> I did not get an email for a case I resolved, can I still complete a response for it in LimeSurvey?

That depends. Many cases that get resolved get filtered out. If you believe that you were supposed to get an email about a certain case, try following the email instructions and use the hive case id in question.

The process of sending emails is done separately from the process of creating responses in LimeSurvey. So, just because you did not receive and email does not mean that the response was not created on your behalf.

If this does not work, then you may manually create your own LimeSurvey response by entering in your token and clicking __Continue__.

> When I go back to the survey response page manually, it doesn't let me enter in another case.

Click the link in the email instead. This will take you to a page that defaults to a new survey response. I believe by default limesurvey puts a cookie on your computer so you go back to the same survey response.

> Why is this so complicated?

Blame LimeSurvey.