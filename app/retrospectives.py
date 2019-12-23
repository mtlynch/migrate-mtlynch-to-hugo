import logging

logger = logging.getLogger(__name__)


def migrate(old_root, new_root):
    logger.info('migrating retrospectives')
