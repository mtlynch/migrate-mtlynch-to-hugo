import collections
import logging
import re

logger = logging.getLogger(__name__)

LegacyImageReference = collections.namedtuple('LegacyImageReference', [
    'src', 'alt', 'fig_caption', 'max_width', 'has_border', 'align', 'link_url'
])


def parse(line, fig_caption_variable):
    fig_caption = _parse_fig_caption(line, fig_caption_variable)
    return LegacyImageReference(src=_parse_attribute(line, 'file'),
                                alt=_parse_attribute(line, 'alt'),
                                fig_caption=fig_caption,
                                max_width=_parse_attribute(line, 'max_width'),
                                has_border=_check_border(line),
                                align=_get_alignment(line),
                                link_url=_parse_attribute(line, 'link_url'))


def _parse_fig_caption(line, fig_caption_variable):
    fig_caption = _parse_attribute(line, 'fig_caption')
    if fig_caption:
        return fig_caption
    if re.search(r'fig_caption\s*=\s*fig_caption', line):
        return fig_caption_variable


def _parse_attribute(line, attribute_name):
    m = re.search(r'%s\s*=\s*"([^"]+)"' % attribute_name, line)
    if m:
        return m.group(1)
    m = re.search(r"%s\s*=\s*'([^']+)'" % attribute_name, line)
    if m:
        return m.group(1)
    return None


def _sanity_check_class_attributes(class_attributes):
    for attr in class_attributes:
        if attr not in ('img-border', 'align-left', 'align-right', 'half',
                        'third'):
            logger.error('Unrecognized class value: %s', attr)


def _parse_class_attributes(line):
    class_attr = _parse_attribute(line, 'class')
    if not class_attr:
        return []
    attrs = class_attr.split(' ')
    _sanity_check_class_attributes(attrs)
    return attrs


def _check_border(line):
    return 'img-border' in _parse_class_attributes(line)


def _get_alignment(line):
    attrs = _parse_class_attributes(line)
    if 'align-left' in attrs:
        return 'left'
    elif 'align-right' in attrs:
        return 'right'
    else:
        return None
