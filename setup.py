from distutils.core import setup

setup(
    name='kanboard-gitlab',
    packages=['kanboard_gitlab'],
    version='0.3',
    description='Script for migrating gitlab issues to kanboard',
    author='Juracy Filho',
    author_email='juracy@gmail.com',
    url='https://github.com/dataprev/kanboard-import-gitlab',
    download_url='https://github.com/dataprev/kanboard-import-gitlab/archive/0.3.tar.gz',
    keywords=['gitlab', 'migration', 'kanboard'],
    classifiers=[],
    scripts=['kanboard_gitlab/kanboard-gitlab'],
)
