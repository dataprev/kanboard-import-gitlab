from distutils.core import setup

version = '0.6'
repo = 'https://github.com/dataprev/kanboard-import-gitlab'

setup(
    name='kanboard-gitlab',
    packages=['kanboard_gitlab'],
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
