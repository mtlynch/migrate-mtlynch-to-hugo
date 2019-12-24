import logging
import os
import shutil

import translate_image_references

logger = logging.getLogger(__name__)


def migrate(old_root, new_root):
    logger.info('migrating about page')

    old_about_path = os.path.join(old_root, '_pages', 'about.md')

    with open(old_about_path) as old_about_file:
        old_contents = old_about_file.read()
        new_contents = old_contents
        new_contents = translate_image_references.translate(new_contents)
        new_contents = _filter_unneeded_frontmatter(new_contents)

    new_about_dir = os.path.join(new_root, 'content', 'about')
    os.makedirs(new_about_dir, exist_ok=True)
    new_about_path = os.path.join(new_about_dir, 'index.md')
    with open(new_about_path, 'w') as new_about_file:
        new_about_file.write(new_contents)

    # Migrate image
    old_image_path = os.path.join(old_root, 'images', 'about',
                                  'author-photo.jpg')
    new_image_path = os.path.join(new_about_dir, 'author-photo.jpg')
    logger.debug('(image) %s -> %s', old_image_path, new_image_path)
    shutil.copyfile(old_image_path, new_image_path)


def _filter_unneeded_frontmatter(contents):
    triple_underscores = 0
    lines = []
    for line in contents.split('\n'):
        if line.startswith('---'):
            triple_underscores += 1
        if triple_underscores == 1:
            if (line.startswith('title:') or line.startswith('header:') or
                    line.startswith('  teaser:')):
                pass
            else:
                continue
        lines.append(line)
    return '\n'.join(lines)
