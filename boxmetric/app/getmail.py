import logging
import time

def init():
    logger = logging.getLogger('project.logging.console')
    logger.info('FDV getmail.init() starts')
    time.sleep(4)
    logger.info('FDV getmail.init() finished')
