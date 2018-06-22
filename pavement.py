"""paver config file"""

# from testing python book
from paver.easy import sh
from paver.tasks import task, needs


@task
def nosetests():
    sh('nosetests --cover-package=Optimizador --cover-tests '
       ' --with-doctest --rednose  ./optimizador/')

@task
def pylint():
    """pyltin"""
    sh('pylint ./optimizador/')

# @task
# def pypi():
#    """Instalation on PyPi"""
#    sh('python setup.py sdist')
#    sh('twine upload dist/*')


# @task
# def sphinx():
#     """Document creation using Shinx"""
#     sh('cd docs; make html; cd ..')

@needs('nosetests', 'pylint')
@task
def default():
    pass
