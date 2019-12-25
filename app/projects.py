import logging
import os

import frontmatter

logger = logging.getLogger(__name__)


def migrate(old_root, new_root):
    logger.info('migrating projects page')

    old_projects_path = os.path.join(old_root, '_pages', 'projects.md')

    with open(old_projects_path) as old_projects_file:
        old_contents = old_projects_file.read()
        new_contents = old_contents
        new_contents = frontmatter.filter_fields(new_contents,
                                                 field_whitelist=['title'])

    new_projects_path = os.path.join(new_root, 'content', 'projects.md')
    with open(new_projects_path, 'w') as new_projects_file:
        new_projects_file.write(new_contents)
