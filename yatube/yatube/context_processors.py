from datetime import datetime as dt


def year(request):
    year = dt.today().year
    return {
        'year': year
    }
