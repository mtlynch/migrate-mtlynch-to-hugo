def make(src, alt=None, caption=None):
    shortcode = '{{< img '
    shortcode += 'src="%s" ' % src
    if alt:
        shortcode += 'alt="%s" ' % alt
    if caption:
        shortcode += 'caption="%s" ' % caption
    shortcode += '>}}'
    return shortcode
