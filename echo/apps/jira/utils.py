import jira


def open_jira_connection():
    return jira.JIRA({'server': 'http://jira.west.com'}, basic_auth=('phemeuser', 'onetwothree'))