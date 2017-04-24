from distutils.core import setup
from kanboard_gitlab import version

repo = 'https://github.com/dataprev/kanboard-import-gitlab'

setup(
    name='kanboard-gitlab',
    packages=['kanboard_gitlab'],
    package_dir={'kanboard_gitlab': 'kanboard_gitlab'},
    package_data={
        'kanboard_gitlab': [
            'locale/pt_BR/LC_MESSAGES/kanboard-gitlab.*',
        ],
    },
    version=version,
    description='Script for migrating gitlab issues to kanboard',
    author='Juracy Filho',
    author_email='juracy@gmail.com',
    url=repo,
    download_url='{}/archive/{}.tar.gz'.format(repo, version),
    keywords=['gitlab', 'migration', 'kanboard'],
    classifiers=[],
    scripts=['kanboard-gitlab'],
    install_requires=[
        'envparse==0.2.0',
        'kanboard==1.0.1',
        'python-gitlab==0.20',
    ],
)
