

def timedelta_to_str(td):
    result = ''
    td = str(td).split(',')
    if len(td) > 1:
        td.pop(0)
        result += td[0] + ' '
    time = td[0].split(':')

    result += '%s hrs ' % time[0]
    result += '%s min ' % time[1]
    result += '%s sec' % time[2].split('.')[0]

    return result
