import distutils.dir_util
import logging
import os

import anchor_links
import blank_lines
import frontmatter
import translate_image_references
import youtube

logger = logging.getLogger(__name__)


def migrate(old_root, new_root):
    logger.info('migrating retrospectives')
    old_retrospectives_dir = os.path.join(old_root, '_retrospectives')
    new_retrospectives_dir = os.path.join(new_root, 'content', 'retrospectives')

    for retrospective_filename in os.listdir(old_retrospectives_dir):
        old_retrospective_path = os.path.join(old_retrospectives_dir,
                                              retrospective_filename)
        date = retrospective_filename[:10]
        if retrospective_filename.find('-pygotham') >= 0:
            slug = 'pygotham-2019-notes'
        elif retrospective_filename.find('-pytexas') >= 0:
            slug = 'pytexas-2019-notes'
        else:
            slug = retrospective_filename[:7]
        if slug.startswith('py'):
            new_retrospective_dir = os.path.join(new_retrospectives_dir, slug)
        else:
            year, month = slug.split('-')
            new_retrospective_dir = os.path.join(new_retrospectives_dir, year,
                                                 month)
        os.makedirs(new_retrospective_dir, exist_ok=True)
        new_retrospective_path = os.path.join(new_retrospective_dir, 'index.md')

        logger.debug('(retrospective) %s -> %s', old_retrospective_path,
                     new_retrospective_path)
        with open(old_retrospective_path) as old_retrospective:
            contents = old_retrospective.read()

        contents = frontmatter.translate_fields(contents,
                                                {'excerpt': 'description'})
        contents = frontmatter.filter_fields(
            contents, field_whitelist=['title', 'description', 'images'])
        contents = frontmatter.insert_field(contents, 'date', date)
        contents = translate_image_references.translate(contents)
        contents = _convert_inline_attribute_lists(contents)
        contents = anchor_links.convert(contents)
        contents = _strip_one_line_summary(contents)
        contents = youtube.iframes_to_shortcodes(contents)
        contents = blank_lines.collapse(contents)

        with open(new_retrospective_path, 'w') as new_retrospective:
            new_retrospective.write(contents)
    _migrate_images(old_root, new_root)


def _convert_inline_attribute_lists(contents):
    lines = []
    for line in contents.split('\n'):
        if not line.startswith('{:'):
            lines.append(line)
            continue
        if line.find('start="') >= 0:
            # Skip ordered list renumberings because Hugo's renderer handles
            # numbering more cleanly.
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

        lines.insert(
            _find_last_blank_line(lines, start=len(lines) - 1) + 1,
            '{{<notice type="%s">}}' % notice_type)
        lines.append('{{< /notice >}}')

    return '\n'.join(lines)


def _strip_one_line_summary(contents):
    lines = []
    ignoring = False
    for line in contents.split('\n'):
        if line.startswith('## One-Line Summary'):
            ignoring = True
        if ignoring:
            if line.startswith('## Highlights'):
                ignoring = False
        if ignoring:
            continue
        lines.append(line)
    return '\n'.join(lines)


def _find_last_blank_line(lines, start):
    for i in range(start, 0, -1):
        if lines[i].strip() == '':
            return i


def _find_next_blank_line(lines, start):
    for i in range(start, len(lines)):
        if lines[i].strip() == '':
            return i


def _migrate_images(old_root, new_root):
    old_images_dir = os.path.join(old_root, 'images', 'retrospectives')
    new_images_dir = os.path.join(new_root, 'content', 'retrospectives')
    distutils.dir_util.copy_tree(old_images_dir, new_images_dir)
