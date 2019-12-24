import logging
import os
import re
import shutil

import img_shortcode
import legacy_image_reference

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

        logger.debug('(post) %s -> %s', old_post_path, new_post_path)
        with open(old_post_path) as old_post:
            old_post_contents = old_post.read()

        new_post_contents = old_post_contents
        new_post_contents = _insert_date_in_frontmatter(new_post_contents, date)
        new_post_contents = _convert_image_references(new_post_contents)
        new_post_contents = _convert_inline_attribute_lists(new_post_contents)

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
    fig_caption_variable = None
    for line in contents.split('\n'):
        if line.startswith('{% assign fig_caption'):
            fig_caption_variable = _parse_fig_caption_variable(line)
            continue
        if line.startswith('{% include image.html'):
            line = _convert_image_reference(line, fig_caption_variable)
        lines.append(line)
    return '\n'.join(lines)


def _convert_inline_attribute_lists(contents):
    lines = []
    for line in contents.split('\n'):
        if not line.startswith('{:'):
            lines.append(line)
            continue
        if line.startswith('{: .clearfix}'):
            # Ignore clearfix, as we're handling it entirely in CSS now.
            continue
        if line.startswith('{: .notice--info}'):
            notice_type = 'info'
        elif line.startswith('{: .notice--warning}'):
            notice_type = 'warning'
        elif line.startswith('{: .notice--danger}'):
            notice_type = 'danger'
        elif line.startswith('{: .notice--success}'):
            notice_type = 'success'
        else:
            logger.warning('Unrecognized IAL: %s', line.strip())
            continue

        lines.insert(len(lines) - 1, '{{<notice type="%s">}}' % notice_type)
        lines.append('{{< /notice >}}')

    return '\n'.join(lines)


def _parse_fig_caption_variable(line):
    m = re.search(r'fig_caption\s*=\s*"([^"]+)"', line)
    if m:
        return _escape_quotes(m.group(1))
    m = re.search(r"fig_caption\s*=\s*'([^']+)'", line)
    if m:
        return _escape_quotes(m.group(1))
    raise ValueError('No fig_caption variable assignment found')


def _escape_quotes(s):
    return s.replace('“', '"').replace('”', '"').replace('"', '\\"')


def _convert_image_reference(old_image_reference, fig_caption_variable):
    legacy_reference = legacy_image_reference.parse(old_image_reference,
                                                    fig_caption_variable)
    return img_shortcode.make(src=legacy_reference.src,
                              alt=legacy_reference.alt,
                              caption=legacy_reference.fig_caption,
                              max_width=legacy_reference.max_width,
                              has_border=legacy_reference.has_border,
                              align=legacy_reference.align)


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
        logger.debug('(image) %s -> %s', old_image_path, new_image_path)
        shutil.copyfile(old_image_path, new_image_path)
