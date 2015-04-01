from base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'TEST_NAME': 'test_database.db'
    }
}

INSTALLED_APPS += ('discover_jenkins',)

TEST_RUNNER = 'discover_jenkins.runner.DiscoverCIRunner'

TEST_PROJECT_APPS = (
    'echo.apps.activity',
    'echo.apps.core',
    'echo.apps.elpis',
    'echo.apps.projects',
    'echo.apps.reports',
    'echo.apps.settings',
    'echo.apps.usage'
)

TEST_TASKS = (
    'discover_jenkins.tasks.with_coverage.CoverageTask',
    'discover_jenkins.tasks.run_pylint.PyLintTask',
)

TEST_COVERAGE_EXCLUDES_FOLDERS = [
    '/usr/local/*',
    'echo/apps/*/tests/*',
]

