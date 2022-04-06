import json
import re
from copy import deepcopy
from urllib.parse import urlencode

import scrapy
from scrapy.http import HtmlResponse

from instscraper.items import InstscraperItem


class InstcomSpider(scrapy.Spider):
    name = 'instcom'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']

    login_link = 'https://www.instagram.com/accounts/login/ajax/'
    password = '#PWD_INSTAGRAM_BROWSER:10:1649179435:AeRQADTfJVo2WnDcUYVtNe4+D2rswpvP0QBx4noYJRzvZEd+' \
               'AZxd04Jw5GmNP5OReOJXsdrbG3/YOg0z1lvhsr+tqJ8uhugJ8HiUc5gcouVPcKLdixmC+n2kS6T/vOQmRz' \
               'Hlo2BGwwa7TAAQXQkltHs='
    username = 'sergey.s.test.2022'
    follow_link = 'https://i.instagram.com/api/v1/friendships'
    follow_list = ['following', 'followers']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.acc_parse_list = kwargs.get('accounts')

    def parse(self, response: HtmlResponse):
        csrf_token = self.get_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.login_link,
            method='POST',
            callback=self.login,
            formdata={
                'enc_password': self.password,
                'username': self.username
            },
            headers={'X-CSRFToken': csrf_token}
        )

    def login(self, response: HtmlResponse):
        j_data = response.json()
        print(j_data)
        if j_data['authenticated']:
            for account in self.acc_parse_list:
                yield response.follow(
                    f'/{account}',
                    callback=self.user_data_parse,
                    cb_kwargs={
                        'username': account
                    }
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.get_user_id(response.text, username)
        variables = {
            'count': 12
        }

        for follow_item in self.follow_list:
            if follow_item == 'followers':
                variables['search_surface'] = 'follow_list_page'

            url_follow = f'{self.follow_link}/{user_id}/{follow_item}/?{urlencode(variables)}'
            followers = follow_item

            yield response.follow(
                url_follow,
                callback=self.user_follow_parse,
                cb_kwargs={
                    'username': username,
                    'user_id': user_id,
                    'variables': deepcopy(variables),
                    'followers': followers
                }
            )

    def user_follow_parse(self, response: HtmlResponse, username, user_id, variables, followers):
        j_data = response.json()
        if j_data.get('big_list'):
            variables['max_id'] = j_data.get('next_max_id')
            url_follow = f'{self.follow_link}/{user_id}/{followers}/?{urlencode(variables)}'

            yield response.follow(
                url_follow,
                callback=self.user_follow_parse,
                cb_kwargs={
                    'username': username,
                    'user_id': user_id,
                    'variables': deepcopy(variables),
                    'followers': followers
                }
            )
        f_users = j_data.get('users')
        for user in f_users:
            item = InstscraperItem(
                user_id=user_id,
                username=username,
                f_user_id=user.get('pk'),
                f_username=user.get('username'),
                f_full_name=user.get('full_name'),
                f_photo=user.get('profile_pic_url'),
                follow=followers
            )
            yield item

    @staticmethod
    def get_csrf_token(text):
        """Получает csrf токен из строки"""
        token = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return token.split(':').pop().replace(r'"', '')

    @staticmethod
    def get_user_id(text, username):
        try:
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except Exception as err:
            print(err)
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]
