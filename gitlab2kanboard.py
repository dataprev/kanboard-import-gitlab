#!/usr/bin/env python
from kanboard import Kanboard
from gitlab import Gitlab, requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class GitlabImporter(object):
    def __init__(self):
        # TODO: It should be optional
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def setup_gitlab(self, endpoint, token):
        self.gitlab = {
            'endpoint': endpoint,
            'token': token,
        }

    def setup_kanboard(self, endpoint, user, token):
        self.kanboard = {
            'endpoint': endpoint,
            'user': user,
            'token': token,
        }

    def connect(self):
        self.gl = Gitlab(
            self.gitlab['endpoint'], self.gitlab['token'], ssl_verify=False)
        self.gl.auth()

        self.kb = Kanboard(
            self.kanboard['endpoint'],
            self.kanboard['user'],
            self.kanboard['token'])

    def migrate(self, namespace, project):
        group = self.gl.groups.list(search=namespace)[0]
        origin = group.projects.list(search=project)[0]

        self.target = self.kb.createProject(name='import')
        print('Projeto {} criado !'.format(self.target))
        self.project_users = self.kb.getProjectUsers(project_id=self.target)
        columns = self.kb.getColumns(project_id=self.target)
        todo = [c for c in columns if c['title'] in ('A fazer')][0]['id']
        doing = [
            c
            for c in columns
            if c['title'] in ('Em andamento', 'Fazendo')][0]['id']
        done = [c for c in columns if c['title'] in ('Done', 'Feito')][0]['id']
        self.users = self.kb.getAllUsers()
        for issue in origin.issues.list(all=True):
            creator = self.get_user_id(issue.author.username)
            owner = None
            if issue.assignee:
                owner = self.get_user_id(issue.assignee.username)
            params = {
                'title': issue.title,
                'project_id': self.target,
                'description': issue.description,
                'reference': '#{}'.format(issue.iid),
                'tags': issue.labels,
                'date_due': issue.due_date,
            }

            if creator:
                params['creator_id'] = self.check_member(creator)

            if owner:
                params['owner_id'] = self.check_member(owner)

            if 'To Do' in issue.labels:
                params['column_id'] = todo
                params['tags'].remove('To Do')

            if 'Doing' in issue.labels:
                params['column_id'] = doing
                params['tags'].remove('Doing')

            if (issue.state == 'closed'):
                params['column_id'] = done

            if not params['tags']:
                del params['tags']

            task = self.kb.createTask(**params)
            if not task:
                print('Oops: ', issue.iid, ' => ', task)

            for comment in issue.notes.list(all=True):
                commenter_id = self.get_user_id(
                    comment.author.username) or self.users[0]['id']
                self.kb.createComment(
                    task_id=task,
                    user_id=commenter_id,
                    content=comment.body,
                )

            if (issue.state == 'closed' and task):
                self.kb.closeTask(task_id=task)

    def check_member(self, member):
        if str(member) not in self.project_users:
            self.kb.addProjectUser(project_id=self.target, user_id=member)
            self.project_users = self.kb.getProjectUsers(
                project_id=self.target)
        return member

    def get_user_id(self, username):
        found = [u['id'] for u in self.users if u['username'] == username]
        if found:
            return found[0]


def main():
    import sys
    from envparse import env

    importer = GitlabImporter()
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
