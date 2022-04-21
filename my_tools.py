from http.client import NON_AUTHORITATIVE_INFORMATION


def parse_pagenum(s):
    s = s.replace('，', ',')
    s = s.replace('—', '-')
    group = s.split(',')
    temp = set()
    for each in group:
        if '-' in each:
            nums = [x for x in each.split('-') if x]
            if len(nums) == 2 and nums[0].isdigit() and nums[1].isdigit():
                temp.update(set(range(int(nums[0]), int(nums[1]) + 1)))
            else:
                return None
        elif each.isdigit():
            temp.add(int(each))
        else:
            return None
    output = sorted(list(temp))
    return output

def under_by(l, max):
    '''
    ``l`` is a list which include page numbers, start by 1. 
    ``max`` is the max page number.
    '''
    if max >= l[-1]:
        return l 
    length = len(l)
    if length <= 3:
        return [x for x in l if x <= max]
    p_start = 0
    p_end = length - 1
    while not (p_start + 1 == p_end):
        if l[(p_start + p_end) // 2] <= max:
            p_start = (p_start + p_end) // 2
        else:
            p_end = (p_start + p_end) // 2
    return l[:p_end]


def export_pagenum(l):
    temp_start = -1
    temp_end = -1
    output = list()
    for num in l:
        if temp_end + 1 == num:
            temp_end = num
        else:
            if temp_end != -1:
                if temp_end > temp_start:
                    output.append('{}-{}'.format(temp_start, temp_end))
                else:
                    output.append('{}'.format(temp_start))
            temp_start = num
            temp_end = num
    if temp_end > temp_start:
        output.append('{}-{}'.format(temp_start, temp_end))
    else:
        output.append('{}'.format(temp_start))

    return ','.join(output)
