import re
from kanboard import Kanboard
from gitlab import Gitlab, requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from gettext import gettext as _


class GitlabImporter(object):
    def __init__(self, label_to_columns):
        self.label_to_columns = label_to_columns
        self.findlabel = re.compile(r'~([0-9]+)')

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
        _groups = [
            g for g in self.gl.groups.search(namespace) if g.name == namespace]
        if not _groups:
            print(_('Error: namespace {} not found !').format(namespace))
            return False
        group = _groups[0]

        _projects = [
            p for p in group.projects.list(search=project) if p.name == project]
        if not _projects:
            print(_('Error: project {} not found in namespace {} !').format(
                project, namespace))
            return False

        origin = _projects[0]

        count = 0
        self.target = self.kb.createProject(
            name='{}/{}'.format(namespace, project))
        print(_('Project {}/{} created, id: {} !').format(
            namespace, project, self.target))
        self.project_users = self.kb.getProjectUsers(project_id=self.target)
        self.columns = self.kb.getColumns(project_id=self.target)
        self.users = self.kb.getAllUsers()
        self.labels = origin.labels.list(all=True)
        for issue in reversed(origin.issues.list(all=True)):
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

            for label, column in self.label_to_columns.items():
                if label in issue.labels:
                    params['column_id'] = self.get_column(column)
                    params['tags'].remove(label)

            if (issue.state == 'closed'):
                params['column_id'] = self.get_column(_('Done'))

            if not params['tags']:
                del params['tags']

            task = self.kb.createTask(**params)
            if task:
                for comment in issue.notes.list(all=True):
                    body = comment.body
                    if 'label' in body:
                        for l in self.findlabel.findall(body):
                            body = body.replace('~{}'.format(l), self.get_label_by_id(l))

                    commenter_id = self.get_user_id(
                        comment.author.username) or self.users[0]['id']
                    self.kb.createComment(
                        task_id=task,
                        user_id=commenter_id,
                        content=body,
                    )

                if (issue.state == 'closed' and task):
                    self.kb.closeTask(task_id=task)

                count += 1
                print(_('... issue {} migrated to task {} {}').format(
                    issue.iid,
                    task,
                    _('(closed)') if issue.state == 'closed' else ''))
            else:
                print(_('Oops: problem to import {}').format(issue.iid))

        print(_('{} issue(s) migrated !'). format(count))
        return True

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

    def get_column(self, column):
        for c in self.columns:
            if c['title'] == column:
                return c['id']

    def get_label_by_id(self, label):
        # Some old versions of gitlab don't send id :(
        found = [l.name for l in self.labels if l.id == int(label)]
        return found[0] if found else '~{}'.format(label)
