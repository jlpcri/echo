from django.db import models

from echo.apps.projects.models import VoiceSlot


class Ticket(models.Model):
    """Stores data related to Jira tickets connected to a missing or defective voice slot"""
    voiceslot = models.ForeignKey(VoiceSlot)
    issue = models.TextField()

    def open(self):
        """Open a new ticket for a voiceslot that has not had one previously."""
        new_issue = {
            'project': self.voiceslot.language.project.jira_key,
            'summary': self.voiceslot.actions.latest('time').description,
            'description': "{0} {1} prompt: {2}".format('Invalid', self.voiceslot.language.name, self.voiceslot.name),
            'issuetype': {'name': 'Bug'},
            'versions': [],
            'components': [{'name': 'Voice Slot/{0}'.format(self.voiceslot.language.name.title())}]

        }



#  >>> new_issue = {
#          'project': 'TP',
#          'summary': 'Automatically generated issue',
#          'description': 'Description goes here',
#          'issuetype': {'name': 'Bug'},
#          'versions': [{'name': '1.2'}, ],
#          'components': [{'name': 'Application/Code'}, ]
#      }
#  >>> server.create_issue(fields=new_issue)
#  <JIRA Issue: key=u'TP-85', id=u'210971'>
