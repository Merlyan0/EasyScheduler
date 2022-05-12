from datetime import datetime


def check_date(date: str):
    if len(date.split()[0].split('.')) == 3:
        a = datetime(year=int(date.split()[0].split('.')[2]), month=int(date.split()[0].split('.')[1]),
                     day=int(date.split()[0].split('.')[1]))
    elif len(date.split()[0].split('.')) == 2:
        a = datetime(year=datetime.now().year, month=int(date.split()[0].split('.')[1]),
                     day=int(date.split()[0].split('.')[0]))
    else:
        a = datetime(year=datetime.now().year, month=datetime.now().month,
                     day=int(date.split()[0].split('.')[0]))

    a = a.replace(hour=int(date.split()[1].split(":")[0]), minute=int(date.split()[1].split(":")[1]))

    return a
