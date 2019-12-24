import collections
import logging
import re

logger = logging.getLogger(__name__)

LegacyImageReference = collections.namedtuple(
    'LegacyImageReference',
    ['src', 'alt', 'fig_caption', 'max_width', 'has_border', 'align'])


def parse(line):
    return LegacyImageReference(src=_parse_attribute(line, 'file'),
                                alt=_parse_attribute(line, 'alt'),
                                fig_caption=_parse_attribute(
                                    line, 'fig_caption'),
                                max_width=_parse_attribute(line, 'max_width'),
                                has_border=_check_border(line),
                                align=_get_alignment(line))


def _parse_attribute(line, attribute_name):
    m = re.search(r'%s="([^"]+)"' % attribute_name, line)
    if not m:
        return None
    return m.group(1)


def _sanity_check_class_attributes(class_attributes):
    for attr in class_attributes:
        if attr not in ('img-border', 'align-left', 'align-right'):
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
