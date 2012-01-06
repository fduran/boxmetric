from celery.decorators import task

@task()
def load_contacts(account):
    sleep(5)
    return
