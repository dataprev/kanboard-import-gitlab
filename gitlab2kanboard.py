#!/usr/bin/env python
import sys
from gettext import bindtextdomain, textdomain, gettext as _
from envparse import env
from importer import GitlabImporter


def main():
    bindtextdomain('gitlab2kanboard', 'locale')
    textdomain('gitlab2kanboard')

    # TODO: Better support for configuring international labels and columns
    labels = {
        'To Do': _('Ready'),
        'Doing': _('Work in progress'),
    }

    importer = GitlabImporter(labels)
    importer.setup_gitlab(env('GITLAB_ENDPOINT'), env('GITLAB_TOKEN'))
    importer.setup_kanboard(
        env('KANBOARD_ENDPOINT'),
        env('KANBOARD_USER', default='jsonrpc'),
        env('KANBOARD_TOKEN'),
    )
    importer.connect()
    importer.migrate(*sys.argv[1].split('/'))


if __name__ == '__main__':
    main()
