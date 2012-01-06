from celery.decorators import task

@task(name="tasks.load_contacts")
def load_contacts(account):
    import logging
    import time
    logger = logging.getLogger('project.logging.console')
    logger.info('FDV task starts for ' + account)
    time.sleep(5)
    logger.info('FDV task ends')
    return
