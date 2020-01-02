import re

import img_shortcode
import legacy_image_reference


def translate(contents):
    lines = []
    fig_caption_variable = None
    for line in contents.split('\n'):
        if line.startswith('{% assign fig_caption'):
            fig_caption_variable = _parse_fig_caption_variable(line)
            continue
        if line.find('{% include image.html') >= 0:
            line = _convert_image_reference(line, fig_caption_variable)
        lines.append(line)
    return '\n'.join(lines)


def _convert_image_reference(old_image_reference, fig_caption_variable):
    leading_spaces = re.match('\s*', old_image_reference).group(0)
    legacy_reference = legacy_image_reference.parse(old_image_reference,
                                                    fig_caption_variable)
    return leading_spaces + img_shortcode.from_legacy_reference(
        legacy_reference)


def _parse_fig_caption_variable(line):
    m = re.search(r'fig_caption\s*=\s*"([^"]+)"', line)
    if m:
        return _escape_quotes(m.group(1))
    m = re.search(r"fig_caption\s*=\s*'([^']+)'", line)
    if m:
        return _escape_quotes(m.group(1))
    raise ValueError('No fig_caption variable assignment found')


def _fix_image_path(line):
    return line.replace('images/', '')


def _escape_quotes(s):
    return s.replace('“', '"').replace('”', '"').replace('"', '\\"')
