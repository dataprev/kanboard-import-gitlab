#!/usr/bin/env python
import sys
from envparse import env
from importer import GitlabImporter


def main():
    # TODO: Better support for configuring international labels and columns
    labels = {
        'To Do': 'A fazer',
        'Doing': 'Em andamento',
    }

    importer = GitlabImporter(labels, 'Feito')
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
