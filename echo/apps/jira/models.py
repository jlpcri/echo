from django.db import models

from echo.apps.projects.models import VoiceSlot
from echo.apps.jira.utils import open_jira_connection


class Ticket(models.Model):
    """Stores data related to Jira tickets connected to a missing or defective voice slot"""
    voiceslot = models.ForeignKey(VoiceSlot)
    issue = models.TextField()

    def open(self, version_name):
        """Open a new ticket for a voiceslot that has not had one previously."""
        new_issue = {
            'project': self.voiceslot.language.project.jira_key,
            'summary': self.voiceslot.history_list().latest('time').description,
            'description': "{0} {1} prompt: {2}".format('Invalid', self.voiceslot.language.name, self.voiceslot.name),
            'issuetype': {'name': 'Bug'},
            'versions': [{'name': version_name}],
            'components': [{'name': 'Voice Slot/{0}'.format(self.voiceslot.language.name.title()
                                                            if self.voiceslot.language.name.title() in ('English', 'Spanish')
                                                            else 'Other')}]
        }

        server = open_jira_connection()
        server.create_issue(fields=new_issue)
        return

# >>> j = jira.JIRA({'server': 'http://jira.west.com'}, basic_auth=('phemeuser', 'onetwothree'))
# >>> j.current_user()
# 'phemeuser'
# >>> p = j.project('TP')
# >>> p
# <JIRA Project: key=u'TP', name=u'TestProject', id=u'13921'>
# >>> p.versions
# [<JIRA Version: name=u'1.0', id=u'18382'>, <JIRA Version: name=u'1.1', id=u'18383'>, <JIRA Version: name=u'1.2', id=u'18394'>, <JIRA Version: name=u'1.3', id=u'18850'>, <JIRA Version: name=u'1.4', id=u'18851'>]
# >>> new_issue = {
#          'project': 'TP',
#          'summary': 'Automatically generated issue',
#          'description': 'Description goes here',
#          'issuetype': {'name': 'Bug'},
#          'versions': [{'name': '1.2'}, ],
#          'components': [{'name': 'Application/Code'}, ]
#      }
# >>> server.create_issue(fields=new_issue)
# <JIRA Issue: key=u'TP-85', id=u'210971'>
