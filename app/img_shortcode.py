def from_legacy_reference(legacy_reference):
    shortcode_parts = ['{{< img']

    attrsMap = {
        'src': legacy_reference.src,
        'alt': legacy_reference.alt,
        'caption': legacy_reference.fig_caption,
        'maxWidth': legacy_reference.max_width,
        'hasBorder': legacy_reference.has_border,
        'align': legacy_reference.align,
        'linkUrl': legacy_reference.link_url,
    }
    attrs = [(k, v) for (k, v) in attrsMap.items() if v]
    for attr_name, attr_value in attrs:
        shortcode_parts.append('%s="%s"' % (attr_name, attr_value))

    shortcode_parts.append('>}}')
    return ' '.join(shortcode_parts)
