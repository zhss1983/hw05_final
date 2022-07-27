from django.core.paginator import Paginator
from django.conf import settings


def my_paginator(
        page_list,
        page_number,
        delta_count=settings.DELTA_PAGE_COUNT,
        count=settings.MAX_PAGE_COUNT,
):
    """Return dictionary of variables for the paginator.

    It is necessary to display the first, last page, the current one and 'delta_count' pages before and after current
    one. 'count' is a maximum posts per page.
    """
    paginator = Paginator(page_list, count)
    page = paginator.get_page(page_number)
    from_page = max(page.number - delta_count, 2)
    to_page = min(page.number + delta_count, paginator.num_pages - 1)
    return {
        'from_page': from_page,
        'to_page': to_page,
        'page': page,
    }
