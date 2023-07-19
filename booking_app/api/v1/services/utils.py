from datetime import datetime
from http import HTTPStatus
from typing import List

import aiohttp
import requests
from pytz import utc

from booking_app.settings import settings


def get_paginate_obj_list(objs, page_numb=1):
    objs_count = len(objs)
    total_page_numbers = objs_count // settings.page_size
    if objs_count % settings.page_size > 0:
        total_page_numbers += 1
    if page_numb > total_page_numbers:
        return []
    return objs[
        settings.page_size * page_numb
        - settings.page_size: settings.page_size * page_numb
    ]


async def get_users_logins(users_ids: List):
    users_data = []
    try:
        for _ in range(settings.number_of_tries_to_get_response):
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.get_users_info_host.format(
                        page=1,
                        field="login",
                    ),
                    json={"ids": users_ids},
                ) as response:
                    if response.status != HTTPStatus.OK:
                        continue
                    data = await response.json()
                    for user_id in users_ids:
                        if user_id not in data:
                            continue
                        login = data[user_id]
                        if isinstance(login, str):
                            users_data.append({"id": user_id, "login": login})
            return True, users_data
    except requests.exceptions.ConnectionError:
        return False, "get user info error"


def change_date_str_to_utc_format(date_str):
    timezone = utc
    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return timezone.localize(date)
