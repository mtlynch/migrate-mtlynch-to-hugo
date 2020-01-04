import logging
import os
import re
import shutil

import anchor_links
import blank_lines
import file_include
import frontmatter
import translate_image_references
import youtube

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
            contents = old_post.read()

        contents = frontmatter.insert_field(contents, 'date', date)
        contents = translate_image_references.translate(contents)
        contents = _convert_inline_attribute_lists(contents)
        contents = _convert_quoted_snippets(contents)
        contents = anchor_links.convert(contents)
        contents = _fix_file_link_paths(contents)
        contents = _fix_tag_links(contents)
        contents = _translate_zestful_ads(contents)
        contents = _translate_greenpithumb_diagrams(contents)
        contents = _strip_raw_directives(contents)
        contents = file_include.to_inline_file_shortcode(contents)
        contents = youtube.iframes_to_shortcodes(contents)
        contents = frontmatter.translate_fields(contents, {
            'last_modified_at': 'lastmod',
            'excerpt': 'description'
        })
        contents = blank_lines.collapse(contents)

        with open(new_post_path, 'w') as new_post:
            new_post.write(contents)
        _migrate_images(old_root, new_root, slug)
    _migrate_files(old_root, new_root)
    _migrate_ymls(old_root, new_root)


def _convert_inline_attribute_lists(contents):
    lines = []
    for line in contents.split('\n'):
        if not line.startswith('{:'):
            lines.append(line)
            continue
        if line.startswith('{: .clearfix}'):
            # Ignore clearfix, as we're handling it entirely in CSS now.
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

        last_blank_line = _find_last_blank_line(lines, start=len(lines) - 1)
        # Special case for /windows-sia-mining
        for i in range(last_blank_line, len(lines)):
            lines[i] = lines[i].replace(' <br/> <br/>', '\n')
        lines.insert(
            _find_last_blank_line(lines, start=len(lines) - 1) + 1,
            '{{<notice type="%s">}}' % notice_type)
        lines.append('{{< /notice >}}')

    return '\n'.join(lines)


def _convert_quoted_snippets(contents):
    lines = contents.split('\n')
    for i, line in enumerate(lines):
        if not line.startswith('>```'):
            continue
        start = _find_last_blank_line(lines, i - 1)
        end = _find_next_blank_line(lines, i + 1)
        for i in range(start, end + 1):
            lines[i] = re.sub(r'^>', '', lines[i])
        lines.insert(end, '{{</quoted-markdown>}}')
        lines.insert(start + 1, '{{<quoted-markdown>}}')
    return '\n'.join(lines)


def _fix_file_link_paths(contents):
    lines = []
    for line in contents.split('\n'):
        fixed = line
        fixed = re.sub(r'\]\(/files/([^/]+/)?', '](', fixed)
        fixed = re.sub(r'src="/files/([^/]+/)?', 'src="', fixed)
        lines.append(fixed)
    return '\n'.join(lines)


def _fix_tag_links(contents):
    lines = []
    for line in contents.split('\n'):
        lines.append(line.replace('/tags/#', '/tags/'))
    return '\n'.join(lines)


def _translate_zestful_ads(contents):
    return contents.replace('{% include ads.html title="zestful" %}',
                            '{{<zestful-ad>}}')


def _translate_greenpithumb_diagrams(contents):
    translated = contents
    replacements = [
        [
            """
{% capture fig_img %}
![GreenPiThumb software architecture](https://docs.google.com/drawings/d/1vY9YU9fFoyrKUh8pRe6gN0bLD1JFDq5ngkTh7yOQrOA/export/png)
{% endcapture %}

{% capture fig_caption %}
GreenPiThumb software architecture
{% endcapture %}

<figure>
  {{ fig_img | markdownify | remove: "<p>" | remove: "</p>" }}
  <figcaption>{{ fig_caption | markdownify | remove: "<p>" | remove: "</p>" }}</figcaption>
</figure>
""".strip(), """
{{< img src="https://docs.google.com/drawings/d/1vY9YU9fFoyrKUh8pRe6gN0bLD1JFDq5ngkTh7yOQrOA/export/png" alt="GreenPiThumb software architecture" caption="GreenPiThumb software architecture" >}}
""".strip()
        ],
        [
            """
{% capture fig_img %}
[![GreenPiThumb wiring diagram](https://raw.githubusercontent.com/JeetShetty/GreenPiThumb/master/doc/greenpithumb_wiring.png)](https://raw.githubusercontent.com/JeetShetty/GreenPiThumb/master/doc/greenpithumb_wiring.png)
{% endcapture %}

{% capture fig_caption %}
GreenPiThumb wiring diagram ([downloadable file](https://github.com/JeetShetty/GreenPiThumb/tree/master/doc))
{% endcapture %}

<figure>
  {{ fig_img | markdownify | remove: "<p>" | remove: "</p>" }}
  <figcaption>{{ fig_caption | markdownify | remove: "<p>" | remove: "</p>" }}</figcaption>
</figure>
    """.strip(), """
{{< img src="https://raw.githubusercontent.com/JeetShetty/GreenPiThumb/master/doc/greenpithumb_wiring.png)](https://raw.githubusercontent.com/JeetShetty/GreenPiThumb/master/doc/greenpithumb_wiring.png" alt="GreenPiThumb wiring diagram" caption="GreenPiThumb wiring diagram ([downloadable file](https://github.com/JeetShetty/GreenPiThumb/tree/master/doc))" >}}
    """.strip()
        ],
    ]
    for old, new in replacements:
        translated = translated.replace(old, new)
    return translated


def _strip_raw_directives(contents):
    return contents.replace('{% raw %}', '').replace('{% endraw %}', '')


def _find_last_blank_line(lines, start):
    for i in range(start, 0, -1):
        if lines[i].strip() == '':
            return i


def _find_next_blank_line(lines, start):
    for i in range(start, len(lines)):
        if lines[i].strip() == '':
            return i


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


def _migrate_files(old_root, new_root):
    for file_dir in ['_files', 'files']:
        old_files_dir = os.path.join(old_root, file_dir)

        for directory in os.listdir(old_files_dir):
            full_dir = os.path.join(old_files_dir, directory)
            if not os.path.isdir(full_dir):
                continue

            new_files_dir = os.path.join(new_root, 'content', 'posts',
                                         directory)

            for filename in os.listdir(full_dir):
                old_path = os.path.join(full_dir, filename)
                _, file_extension = os.path.splitext(filename)
                read_write_suffix = ''
                if file_extension in ['.pdf', '.mp4']:
                    read_write_suffix = 'b'
                with open(old_path, 'r' + read_write_suffix) as old_file:
                    contents = old_file.read()

                if file_dir == '_files':
                    contents = frontmatter.remove(contents)
                new_path = os.path.join(new_files_dir, filename)
                with open(new_path, 'w' + read_write_suffix) as new_file:
                    new_file.write(contents)

        # Migrate stray files.
        migrations = {
            'GreenPiThumb.pdf': 'editor',
            'Multi-article-notes.pdf': 'editor',
            'provision-vm-host.yml': 'building-a-vm-homelab',
            'Sia-NAS.pdf': 'editor',
            'SiaMiningTask.xml': 'windows-sia-mining',
            'TaskRabbit.pdf': 'editor',
        }
        for filename, destination_dir in migrations.items():
            source_path = os.path.join(old_root, 'files', filename)
            dest_path = os.path.join(new_root, 'content', 'posts',
                                     destination_dir, filename)
            shutil.copyfile(source_path, dest_path)


def _migrate_ymls(old_root, new_root):
    old_ymls_dir = os.path.join(old_root, '_ymls')

    for directory in os.listdir(old_ymls_dir):
        full_dir = os.path.join(old_ymls_dir, directory)
        if not os.path.isdir(full_dir):
            continue

        new_files_dir = os.path.join(new_root, 'content', 'posts', directory)
        for yml_filename in os.listdir(full_dir):
            old_yml_path = os.path.join(full_dir, yml_filename)
            with open(old_yml_path) as old_yml_file:
                contents = old_yml_file.read()

            contents = frontmatter.remove(contents)

            new_yml_path = os.path.join(new_files_dir, yml_filename + '.yml')
            with open(new_yml_path, 'w') as new_yml_file:
                new_yml_file.write(contents)
