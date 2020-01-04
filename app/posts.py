import logging
import os
import re
import shutil

import anchor_links
import blank_lines
import file_include
import frontmatter
import legacy_image_reference
import translate_image_references
import youtube

logger = logging.getLogger(__name__)


def migrate(old_root, new_root):
    logger.info('migrating posts')
    _migrate_posts(old_root, new_root)
    _migrate_content_writer_pages(old_root, new_root)


def _migrate_posts(old_root, new_root):
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
        contents = _convert_contents(contents)

        with open(new_post_path, 'w') as new_post:
            new_post.write(contents)
        _migrate_images(os.path.join(old_root, 'images', slug), new_post_dir)
    _migrate_files(old_root, new_root)
    _migrate_ymls(old_root, new_root)


def _migrate_content_writer_pages(old_root, new_root):
    old_posts_dir = os.path.join(old_root, '_pages', 'hiring-content-writers')
    new_posts_dir = os.path.join(new_root, 'content', 'guides',
                                 'hiring-content-writers')
    for post_filename in os.listdir(old_posts_dir):
        old_post_path = os.path.join(old_posts_dir, post_filename)
        slug, _ = post_filename.split('.md')
        new_post_dir = os.path.join(new_posts_dir, slug)
        os.makedirs(new_post_dir, exist_ok=True)
        new_post_path = os.path.join(new_post_dir, 'index.md')

        logger.debug('(hiring-content-writers) %s -> %s', old_post_path,
                     new_post_path)
        with open(old_post_path) as old_post:
            contents = old_post.read()

        contents = frontmatter.filter_fields(
            contents, field_whitelist=['title', 'permalink'])
        contents = frontmatter.translate_fields(contents, {'permalink': 'url'})
        contents = frontmatter.insert_field(contents, 'date', '2019-09-30')
        contents = _convert_contents(contents)

        with open(new_post_path, 'w') as new_post:
            new_post.write(contents)
        _migrate_images(
            os.path.join(old_root, 'images', 'hiring-content-writers', slug),
            new_post_dir)


def _convert_contents(old_contents):
    contents = old_contents
    contents = _translate_galleries(contents)
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
    return contents


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


def _translate_galleries(contents):
    translated = contents
    # Just translate the complicated ones with search/replace.
    replacements = [
        [
            """
<figure class="third">
  {% include image.html file="mma-v1.png" alt="MMA cartoon v1" img_link=true %}
  {% include image.html file="mma-v2.png" alt="MMA cartoon v2" img_link=true %}
  {% include image.html file="mma-v3.png" alt="Final version of MMA cartoon" img_link=true %}
  <figcaption>Evolution of "Offer sincere praise" cartoon from <a href="https://mtlynch.io/human-code-reviews-2/#offer-sincere-praise">"How to do Code Reviews Like a Human"</a></figcaption>
</figure>
""".strip(), """
{{< gallery caption="Evolution of \\"Offer sincere praise\\" cartoon from [How to do Code Reviews Like a Human](https://mtlynch.io/human-code-reviews-2/#offer-sincere-praise)" >}}
  {{< bare-img src="mma-v1.png" alt="MMA cartoon v1" >}}
  {{< bare-img src="mma-v2.png" alt="MMA cartoon v2" >}}
  {{< bare-img src="mma-v3.png" alt="Final version of MMA cartoon" >}}
{{< /gallery >}}
""".strip()
        ],
        [
            """
<figure class="half">
  {% include image.html file="spreadsheet-1.jpg" alt="Freelancer hours spreadsheet" img_link="true" media_rendition="half" %}
  {% include image.html file="spreadsheet-2.jpg" alt="Freelancer payment spreadsheet" img_link="true" media_rendition="half" %}
  <figcaption>Simple timesheets and invoicing with <a href="https://docs.google.com/spreadsheets/d/1LDMdzBiNDkiL3EdsOhP9yxDETjcXaRlAXV03Cd6gViI/edit?usp=sharing">Google Sheets</a>.</figcaption>
</figure>
""".strip(), """
{{< gallery caption="Simple timesheets and invoicing with [Google Sheets](https://docs.google.com/spreadsheets/d/1LDMdzBiNDkiL3EdsOhP9yxDETjcXaRlAXV03Cd6gViI/edit?usp=sharing)" >}}
  {{< bare-img src="spreadsheet-1.jpg" alt="Freelancer hours spreadsheet" >}}
  {{< bare-img src="spreadsheet-2.jpg" alt="Freelancer payment spreadsheet" >}}
{{< /gallery >}}
""".strip()
        ],
        [
            """
<figure class="half">
  {% include image.html file="block-news1.jpg" alt="Open uBlock Origin settings" img_link="true" media_rendition="half" %}
  {% include image.html file="block-news2.jpg" alt="Adding Google News as a blocked site in uBlock Origin" img_link="true" media_rendition="half" %}
  <figcaption>Using <a href="https://github.com/gorhill/uBlock">uBlock Origin</a> rules to block Google News.</figcaption>
</figure>
""".strip(), """
{{< gallery caption="Using [uBlock Origin](https://github.com/gorhill/uBlock) rules to block Google News." >}}
  {{< bare-img src="block-news1.jpg" alt="Open uBlock Origin settings" >}}
  {{< bare-img src="block-news2.jpg" alt="Adding Google News as a blocked site in uBlock Origin" >}}
{{< /gallery >}}
""".strip()
        ],
    ]
    for old, new in replacements:
        translated = translated.replace(old, new)
    translated = _translate_simple_galleries(translated)
    return translated


def _translate_simple_galleries(contents):
    lines = []
    raw_lines = contents.split('\n')
    i = 0
    while i < len(raw_lines):
        raw_line = raw_lines[i]
        if ('figure class="half"' in raw_line or
                'figure class="third"' in raw_line):
            gallery_lines, skip_lines = _translate_gallery(raw_lines, i)
            lines.extend(gallery_lines)
            i += skip_lines
        else:
            lines.append(raw_line)
            i += 1
    return '\n'.join(lines)


def _translate_gallery(lines, index):
    i = index + 1
    line = lines[i]
    caption = None
    legacy_images = []
    while line.find('</figure>') < 0:
        if '<figcaption>' in line:
            caption = line.replace('<figcaption>',
                                   '').replace('</figcaption>', '').strip()
        else:
            legacy_images.append(legacy_image_reference.parse(line, None))
        i += 1
        line = lines[i]
    if caption:
        caption_attr = 'caption="%s" ' % caption
    else:
        caption_attr = ''
    gallery_lines = []
    gallery_lines.append('{{< gallery %s>}}' % caption_attr)
    for legacy_image in legacy_images:
        gallery_lines.append('  {{< bare-img src="%s" alt="%s" >}}' %
                             (legacy_image.src, legacy_image.alt))
    gallery_lines.append('{{</ gallery >}}')
    return gallery_lines, (i - index + 1)


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


def _migrate_images(old_images_dir, new_images_dir):
    if not os.path.exists(old_images_dir):
        logger.info('no images for %s', old_images_dir)
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
