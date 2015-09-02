from django.db import models

from echo.apps.projects.models import VoiceSlot
from echo.apps.jira.utils import open_jira_connection


class Ticket(models.Model):
    """Stores data related to Jira tickets connected to a missing or defective voice slot"""
    voiceslot = models.ForeignKey(VoiceSlot)
    issue = models.TextField()

    def open(self, version_name):
        """Open a new ticket for a voiceslot that has not had one previously."""
        server = open_jira_connection()
        language = self.voiceslot.language.name.title() if self.voiceslot.language.name.title() in ('English', 'Spanish') else 'Other'
        components = [c.name for c in server.project(self.voiceslot.language.project.jira_key).components if c.name.endswith(language)]
        new_issue = {
            'project': self.voiceslot.language.project.jira_key,
            'description': self.voiceslot.history_list().latest('time').description,
            'summary': "{0} {1} prompt: {2}".format('Invalid', self.voiceslot.language.name.title(), self.voiceslot.name),
            'issuetype': {'name': 'Bug'},
            'versions': [{'name': version_name}],
            'components': [{'name': components[0]}]
        }


        server.create_issue(fields=new_issue)
        return

    def close(self):
        """Close an existing ticket"""
        server = open_jira_connection()
        issue = server.issue(self.issue)
        if issue.fields.status['name'] in ('Open', 'Reopened'):
            server.transition_issue(issue, '2')  # 2 means 'Close Issue.' Why? Anyone's guess.

        return

    def reopen(self):
        """Reopen an existing ticket"""
        server = open_jira_connection()
        issue = server.issue(self.issue)
        if issue.fields.status['name'] == 'Closed':
            server.transition_issue(issue, '3')

        return
