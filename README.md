Table of contents
=================
1. Introduction
2. Installation
3. Lime Settings
4. Config files
5. End User Instructions 
6. Important Information
7. Common Questions

Introduction
------------
In a nutshell, the hive2lime script takes cases from TheHive that have been marked as _Resolved_ and transfers some of the cases information to a LimeSurvey response. These responses can be accessed at a later date by the person who resolved the case.

Installation
-------------
There is no setup.py currently. You must copy the entire repo to a destination folder.

1. `sudo git clone https://github.com/KMCGamer/hive2lime.git`
2. Go through the configuration files and fill out the information.
3. Set up a cronjob to run `main.py` based on your interval.

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

All configuration options are here. If they are not here, then you will need to modifiy the script. The config files do not use quotes (""). When editing config files, follow the examples below.

### hive.ini

Put all the information for TheHive into the hive.ini file. The URL should be the base url to access TheHive. Do not append a forward slash to the end of it. The username and password are from the api user.

#### Example hive.ini:
```ini
[hive]
url = https://XXX.XXX.XXX.XXX
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
```ini
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

### misc.ini

All miscelaneous information for the script should go in here.

The `script` section is for setting how often you want the script to run and has debugging options.

The `email` section is for sending emails to end users for completion of surveys.

#### Example misc.ini:
```ini
[script]
interval = 86400000
debug = true

[email]
smtp = smtp.server.com
sender = sender@server.com
debug = debugger@server.com
```

End User Instructions
---------------------

### Emails

Users that resolve cases on the hive should automatically get emails with instructions on how to access their LimeSurvey responses.

__In order for the user to recieve emails, their TheHive username must match the username of their mailbox.sc.edu email address!__

A user must do the following to complete their response:

1. Click on the link in the email.
2. Click __Load unfinished survey__ in the navigation bar.
3. Type in a hive case number that has been resolved (these are listed in the email) into the __Saved Name field AND the Password field__. 
4. Complete the survey and submit it.

Important Information
----------------
The create\_json function in the script must be edited in order for it to work on different surveys. Make sure the survey codes line up with your corresponding questions. You can find the survey codes by going into the mysql limesurvey database and describing your limesurvey response table.

```python
def create_json(case, token):
    return {
        "token": token,
        "submitdate": "",
        # Hive reference id.
        "795616X1X1": case['caseId'],
        # When did you start your investigation?
        "795616X1X4": datetime.fromtimestamp(int(case['startDate'] / 1000)).strftime('%Y-%m-%d'),
        # Time to compromise.
        "795616X6X57SQ001": "Y" if "Dwell Time" in case['metrics'] else "",
        "795616X6X57SQ001comment": case['metrics'].get('Dwell Time', ""),
        # Time worked.
        "795616X6X63": case['metrics'].get('Time Worked', "")
    }
```

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
