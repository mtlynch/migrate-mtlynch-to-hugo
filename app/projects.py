import logging
import os

import frontmatter

logger = logging.getLogger(__name__)


def migrate(old_root, new_root):
    logger.info('migrating projects page')

    old_projects_path = os.path.join(old_root, '_pages', 'projects.md')

    with open(old_projects_path) as old_projects_file:
        contents = old_projects_file.read()
        contents = frontmatter.filter_fields(contents,
                                             field_whitelist=['title'])

    new_projects_path = os.path.join(new_root, 'content', 'projects.md')
    with open(new_projects_path, 'w') as new_projects_file:
        new_projects_file.write(contents)
