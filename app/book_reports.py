import logging
import os
import shutil

logger = logging.getLogger(__name__)


def migrate(old_root, new_root):
    logger.info('migrating book reports')
    old_book_reports_dir = os.path.join(old_root, '_book_reports')
    new_book_reports_dir = os.path.join(new_root, 'content', 'book-reports')

    for report_filename in os.listdir(old_book_reports_dir):
        old_report_path = os.path.join(old_book_reports_dir, report_filename)
        slug, _ = report_filename.split('.md')
        new_report_dir = os.path.join(new_book_reports_dir, slug)
        os.makedirs(new_report_dir, exist_ok=True)
        new_report_path = os.path.join(new_report_dir, 'index.md')

        logger.debug('(report) %s -> %s', old_report_path, new_report_path)
        with open(old_report_path) as old_report:
            old_report_contents = old_report.read()

        new_report_contents = old_report_contents
        new_report_contents = _translate_frontmatter(new_report_contents)
        new_report_contents = _filter_clearfix(new_report_contents)

        with open(new_report_path, 'w') as new_report:
            new_report.write(new_report_contents)
        _migrate_images(old_root, new_root, slug)


def _translate_frontmatter(contents):
    triple_underscores = 0
    lines = []
    for line in contents.split('\n'):
        if line.startswith('---'):
            triple_underscores += 1
            lines.append(line)
            continue
        if triple_underscores == 1:
            if line.startswith('read_date: '):
                _, read_date = line.split('read_date: ')
                lines.append('date: \'%s\'' % read_date.strip())
                continue
            elif line.startswith('  score: '):
                _, rating = line.split('  score: ')
                lines.append('rating: %s' % rating.strip())
                continue
            elif line.startswith('  link_url: '):
                _, purchase_url = line.split('  link_url: ')
                lines.append('purchase_url: %s' % purchase_url.strip())
                continue
            elif line.startswith('title: '):
                lines.append(line)
                continue
            else:
                continue
        lines.append(line)
    return '\n'.join(lines)


def _filter_clearfix(contents):
    lines = []
    for line in contents.split('\n'):
        if line.startswith('<div style="clear: both;"></div>'):
            continue
        lines.append(line)
    return '\n'.join(lines)


def _migrate_images(old_root, new_root, slug):
    old_images_dir = os.path.join(old_root, 'images', 'book-reports', slug)
    new_images_dir = os.path.join(new_root, 'content', 'book-reports', slug)
    if not os.path.exists(old_images_dir):
        logger.info('no images for %s', slug)
        return

    # TODO: Special case for hiring-content-writers
    for image_filename in os.listdir(old_images_dir):
        old_image_path = os.path.join(old_images_dir, image_filename)
        if os.path.isdir(old_image_path):
            continue
        new_image_path = os.path.join(new_images_dir, 'cover.jpg')
        logger.debug('(image) %s -> %s', old_image_path, new_image_path)
        shutil.copyfile(old_image_path, new_image_path)
