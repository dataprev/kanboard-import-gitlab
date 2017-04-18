#!/usr/bin/env python
import sys

from kanboard import Kanboard
from gitlab import Gitlab, requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from envparse import env

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

setup_gitlab = {
    'endpoint': env('GITLAB_ENDPOINT'),
    'token': env('GITLAB_TOKEN'),
    'group': sys.argv[1].split('/')[0],
    'project': sys.argv[1].split('/')[1],
}

setup_kanboard = {
    'endpoint': env('KANBOARD_ENDPOINT'),
    'user': env('KANBOARD_USER', default='jsonrpc'),
    'token': env('KANBOARD_TOKEN'),
}

gl = Gitlab(setup_gitlab['endpoint'], setup_gitlab['token'], ssl_verify=False)
gl.auth()

kb = Kanboard(
  setup_kanboard['endpoint'],
  setup_kanboard['user'],
  setup_kanboard['token'])

group = gl.groups.list(search=setup_gitlab['group'])[0]
origin = group.projects.list(search=setup_gitlab['project'])[0]
target = kb.createProject(name='import')
print('Projeto {} criado !'.format(target))
project_users = kb.getProjectUsers(project_id=target)
columns = kb.getColumns(project_id=target)
todo = [c for c in columns if c['title'] in ('A fazer')][0]['id']
doing = [c for c in columns if c['title'] in ('Em andamento', 'Fazendo')][0]['id']
done = [c for c in columns if c['title'] in ('Done', 'Feito')][0]['id']
users = kb.getAllUsers()
for issue in origin.issues.list(all=True):
    creator = [u['id'] for u in users if u['username'] == issue.author.username]
    if issue.assignee:
        owner = [u['id'] for u in users if u['username'] == issue.assignee.username]
    else:
        owner = []
    params = {
       'title': issue.title,
       'project_id': target,
       'description': issue.description,
       'reference': '#{}'.format(issue.iid),
       'tags': issue.labels,
       'date_due': issue.due_date,
    }

    if creator:
        if str(creator[0]) not in project_users:
            kb.addProjectUser(project_id=target, user_id=creator[0])
            project_users = kb.getProjectUsers(project_id=target)
        params['creator_id'] = creator[0]

    if owner:
        if str(owner[0]) not in project_users:
            kb.addProjectUser(project_id=target, user_id=owner[0])
            project_users = kb.getProjectUsers(project_id=target)
        params['owner_id'] = owner[0]

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

    task = kb.createTask(**params)
    if not task:
        print('Oops: ', issue.iid, ' => ', task)

    for comment in issue.notes.list(all=True):
        commenter_id = users[0]['id']
        commenter = [u['id'] for u in users if u['username'] == comment.author.username]
        if commenter:
            commenter_id = commenter[0]
        kb.createComment(
            task_id=task,
            user_id=commenter_id,
            content=comment.body,
        )

    if (issue.state == 'closed' and task):
        kb.closeTask(task_id=task)
