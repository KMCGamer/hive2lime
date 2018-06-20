import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ConfigParser import SafeConfigParser
from string import Template

class MailClient:

    def __init__(self, debug=False):
        parser = SafeConfigParser()
        parser.read('./config/misc.ini')

        self.email = parser.get('email', 'sender')
        self.smtp_addr = parser.get('email', 'smtp')
        self.domain = parser.get('email', 'domain')
        self.debug = debug


    def send(self, person, cases, token):
        """ Sends a notification email for users that have to complete responses.

        Args:
            cases (dict): all the cases that were resolved within the last interval.
            lime_api (dict): contains information like user, pass, surveyid, etc.

        Raises:
            Exception: if email wasn't sent correctly.
        """

        parser = SafeConfigParser()
        parser.read('./config/lime.ini')
        link = "{}/{}?token={}&newtest=Y&lang=en".format(parser.get('misc', 'url'),
                                                         parser.get(
                                                             'misc', 'sid'),
                                                         token)

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        with open("./config/email/subject.txt") as fileobj:
            msg['Subject'] = fileobj.read()
        msg['From'] = self.email
        msg['To'] = '{}@{}'.format(person, self.domain)

        # Create the body of the message (a plain-text and an HTML version).
        with open("./config/email/body.html") as htmlfile:
            html = Template(htmlfile.read()).substitute(person=person,
                                                        cases="<br>".join(
                                                            cases),
                                                        link=link)

        html = MIMEText(html, 'html')
        msg.attach(html)

        smtp = smtplib.SMTP(self.smtp_addr)
        smtp.sendmail(msg['From'], msg['To'], msg.as_string())
        smtp.quit()

    def multisend(self, responses, tokens):
        emaildict = {}
        for response in responses:
            name = response.values()[0]['token']
            case_id = str(response.values()[0]['Q00002'])
            if name not in emaildict:
                emaildict[name] = [case_id]
            else:
                emaildict[name].append(case_id)

        for person in emaildict:
            self.send(person, emaildict[person], tokens[person])
            break
