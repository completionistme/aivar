import os

CEND = '\33[0m'
CBOLD = '\33[1m'
CITALIC = '\33[3m'
CURL = '\33[4m'
CBLINK = '\33[5m'
CBLINK2 = '\33[6m'
CSELECTED = '\33[7m'

CBLACK = '\33[30m'
CRED = '\33[31m'
CGREEN = '\33[32m'
CYELLOW = '\33[33m'
CBLUE = '\33[34m'
CVIOLET = '\33[35m'
CBEIGE = '\33[36m'
CWHITE = '\33[37m'

CBLACKBG = '\33[40m'
CREDBG = '\33[41m'
CGREENBG = '\33[42m'
CYELLOWBG = '\33[43m'
CBLUEBG = '\33[44m'
CVIOLETBG = '\33[45m'
CBEIGEBG = '\33[46m'
CWHITEBG = '\33[47m'

CGREY = '\33[90m'
CRED2 = '\33[91m'
CGREEN2 = '\33[92m'
CYELLOW2 = '\33[93m'
CBLUE2 = '\33[94m'
CVIOLET2 = '\33[95m'
CBEIGE2 = '\33[96m'
CWHITE2 = '\33[97m'

CGREYBG = '\33[100m'
CREDBG2 = '\33[101m'
CGREENBG2 = '\33[102m'
CYELLOWBG2 = '\33[103m'
CBLUEBG2 = '\33[104m'
CVIOLETBG2 = '\33[105m'
CBEIGEBG2 = '\33[106m'
CWHITEBG2 = '\33[107m'


def section(*texts, end='\n'):
    for text in texts:
        if os.name == 'nt':
            print(text, end=end)
        else:
            print(CBOLD + CVIOLET2 + text + CEND, end=end)


def section_end(*texts, end='\n'):
    for text in texts:
        if os.name == 'nt':
            print(text, end=end)
        else:
            print(CBOLD + CVIOLET + text + CEND, end=end)
    print()


def info(*texts, end='\n'):
    for text in texts:
        if os.name == 'nt':
            print(text, end=end)
        else:
            print(CBLUE + text + CEND, end=end)


def success(*texts, end='\n'):
    for text in texts:
        if os.name == 'nt':
            print(text, end=end)
        else:
            print(CGREEN + text + CEND, end=end)


def highlight(*texts, end='\n'):
    for text in texts:
        if os.name == 'nt':
            print(text, end=end)
        else:
            print(CBOLD + CYELLOW2 + text + CEND, end=end)


def warn(*texts, end='\n'):
    for text in texts:
        if os.name == 'nt':
            print(text, end=end)
        else:
            print(CYELLOW + text + CEND, end=end)


def error(*texts, end='\n'):
    for text in texts:
        if os.name == 'nt':
            print(text, end=end)
        else:
            print(CRED + text + CEND, end=end)


# from: https://stackoverflow.com/a/34325723/580651
# from: https://stackoverflow.com/a/27871113/580651
def progress(iteration, total, decimals=1, length=60, fill='█'):
    # bar_len = 60
    # filled_len = int(round(bar_len * count / float(total)))
    #
    # percents = round(100.0 * count / float(total), 1)
    # bar = '=' * filled_len + '-' * (bar_len - filled_len)
    #
    # # print('\r'+str(count), end=' ', flush=True) # this is the only way to flush it on macos ... wth
    # print("\r[%s] %s%s" % (bar, percents, '%'), end=' ', flush=True)
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    #info('\r|%s| %s/%s %s%%' % (bar, iteration, total, percent), end=' ')
    if os.name == 'nt':
        end = '\r'
    else:
        end = ' '
    info('\r|%s| %s/%s %s%%' % (bar, iteration, total, percent), end=end)
    # Print New Line on Complete
    if iteration == total:
        print()
