def collapse(contents):
    lines = []
    last_line_was_blank = False
    for line in contents.split('\n'):
        if line.strip() == '':
            if last_line_was_blank:
                continue
            last_line_was_blank = True
        else:
            last_line_was_blank = False
        lines.append(line)
    return '\n'.join(lines)
