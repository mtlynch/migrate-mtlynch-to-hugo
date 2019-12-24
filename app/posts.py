import logging
import os
import re
import shutil

logger = logging.getLogger(__name__)


def migrate(old_root, new_root):
    logger.info('migrating posts')
    old_posts_dir = os.path.join(old_root, '_posts')
    new_posts_dir = os.path.join(new_root, 'content', 'posts')

    for post_filename in os.listdir(old_posts_dir):
        old_post_path = os.path.join(old_posts_dir, post_filename)
        date = post_filename[:10]
        slug, _ = post_filename[11:].split('.md')
        new_post_dir = os.path.join(new_posts_dir, slug)
        os.makedirs(new_post_dir, exist_ok=True)
        new_post_path = os.path.join(new_post_dir, 'index.md')

        logger.info('(post) %s -> %s', old_post_path, new_post_path)
        with open(old_post_path) as old_post:
            old_post_contents = old_post.read()

        new_post_contents = old_post_contents
        new_post_contents = _insert_date_in_frontmatter(new_post_contents, date)
        new_post_contents = _convert_image_references(new_post_contents)

        with open(new_post_path, 'w') as new_post:
            new_post.write(new_post_contents)
        _migrate_images(old_root, new_root, slug)


def _insert_date_in_frontmatter(contents, date):
    triple_underscores = 0
    lines = []
    for line in contents.split('\n'):
        if line.startswith('---'):
            triple_underscores += 1
            if triple_underscores == 2:
                lines.append('date: \'%s\'' % date)
        lines.append(line)
    return '\n'.join(lines)


def _convert_image_references(contents):
    lines = []
    for line in contents.split('\n'):
        if line.startswith('{% include image.html'):
            line = _convert_image_reference(line)
        lines.append(line)
    return '\n'.join(lines)


def _convert_image_reference(old_image_reference):
    filename = re.search(r'file="([^"]+)"', old_image_reference).group(1)
    m = re.search(r'alt="([^"]+)"', old_image_reference)
    if m:
        alt = m.group(1)
    else:
        alt = None
    m = re.search(r'fig_caption="([^"]+)"', old_image_reference)
    if m:
        caption = m.group(1)
    else:
        caption = None

    shortcode = '{{< img '
    shortcode += 'src="%s" ' % filename
    if alt:
        shortcode += 'alt="%s" ' % alt
    if caption:
        shortcode += 'caption="%s" ' % caption
    shortcode += '>}}'

    # TODO: Process other image properties.
    return shortcode


#{% include image.html file="clipbucket-install-complete.png" alt="Complete ClipBucket installation" img_link=true %}


def _migrate_images(old_root, new_root, slug):
    old_images_dir = os.path.join(old_root, 'images', slug)
    new_images_dir = os.path.join(new_root, 'content', 'posts', slug)
    if not os.path.exists(old_images_dir):
        logger.info('no images for %s', slug)
        return

    # TODO: Special case for hiring-content-writers
    for image_filename in os.listdir(old_images_dir):
        old_image_path = os.path.join(old_images_dir, image_filename)
        if os.path.isdir(old_image_path):
            continue
        new_image_path = os.path.join(new_images_dir, image_filename)
        logger.info('(image) %s -> %s', old_image_path, new_image_path)
        shutil.copyfile(old_image_path, new_image_path)
