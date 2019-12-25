import logging
import os

logger = logging.getLogger(__name__)


def migrate(old_root, new_root):
    logger.info('migrating projects page')

    old_projects_path = os.path.join(old_root, '_pages', 'projects.md')

    with open(old_projects_path) as old_projects_file:
        old_contents = old_projects_file.read()
        new_contents = old_contents
        new_contents = _filter_unneeded_frontmatter(new_contents)

    new_projects_path = os.path.join(new_root, 'content', 'projects.md')
    with open(new_projects_path, 'w') as new_projects_file:
        new_projects_file.write(new_contents)


def _filter_unneeded_frontmatter(contents):
    triple_underscores = 0
    lines = []
    for line in contents.split('\n'):
        if line.startswith('---'):
            triple_underscores += 1
            lines.append(line)
            continue
        if triple_underscores == 1:
            if line.startswith('title:'):
                pass
            else:
                continue
        lines.append(line)
    return '\n'.join(lines)
