import scrapy
import re
import json
from copy import deepcopy
from urllib.parse import urlencode
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem


class InstacomSpider(scrapy.Spider):
    name = 'instacom'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'Onliskill_udm'  # Qw123456789
    inst_pwd = '#PWD_INSTAGRAM_BROWSER:10:1634577477:AWdQAK0AEOF+wFwWVYjoEuu8uCHn+Pabck9vUxQlFS3/o3VdiZCGuEm4HaF+MLP9EwSytUXe+VNGZWVqv/Pz+z14vr8gT4dClBa6OPYXzPbHCHcU0fUqrO731Bcf4OCxjIcxB4lurkTpWrZPz+Ir'
    user_for_parse_1 = 'onliskill_udm'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    subscribers_hash = 'c76146de99bb02f6415203be841dd25a'
    subscriptions_hash = 'd04b0a864b4b54837c0d870b0e77e076'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login,
                      'enc_password': self.inst_pwd},
            headers={'x-csrftoken': csrf}
        )

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:
            yield response.follow(
                f'/{self.user_for_parse_1}',
                callback=self.user_parse,
                cb_kwargs={'username': self.user_for_parse_1}
            )

    def user_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)

        variables = {'id': user_id, 'username': username, 'first': 12}
        url_subscribers = f'{self.graphql_url}query_hash={self.subscribers_hash}&{urlencode(variables)}'

        yield response.follow(
            url_subscribers,
            callback=self.subscribers_parse,
            cb_kwargs={'user_id': user_id,
                       'username': username,
                       'variables': deepcopy(variables)
                       }
        )

        url_subscriptions = f'{self.graphql_url}query_hash={self.subscriptions_hash}&{urlencode(variables)}'
        yield response.follow(
            url_subscriptions,
            callback=self.subscriptions_parse,
            cb_kwargs={'user_id': user_id,
                       'username': username,
                       'variables': deepcopy(variables)
                       }
        )

    def subscribers_parse(self, response, user_id, username, variables):
        j_data = response.json()
        page_info = j_data.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']
            url_subscribers = f'{self.graphql_url}query_hash={self.subscribers_hash}&{urlencode(variables)}'
            yield response.follow(
                url_subscribers,
                callback=self.subscribers_parse,
                cb_kwargs={'user_id': user_id,
                           'username': username,
                           'variables': deepcopy(variables)}
            )

        subscribers = j_data.get('data').get('user').get('edge_followed_by').get('edges')
        for subscriber in subscribers:
            item = InstaparserItem(
                user_id=user_id,
                user_name=username,
                subscriber_id=subscriber['node']['id'],
                subscriber_name=subscriber['node']['username'],
                subscriber_fullname=subscriber['node']['full_name'],
                photo=subscriber['node']['profile_pic_url'],
                subscriber_type='subscriber'
            )
            yield item

    def subscriptions_parse(self, response, user_id, username, variables):
        j_data = response.json()
        page_info = j_data.get('data').get('user').get('edge_follow').get('page_info')
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']
            url_subscriptions = f'{self.graphql_url}query_hash={self.subscriptions_hash}&{urlencode(variables)}'
            yield response.follow(
                url_subscriptions,
                callback=self.subscriptions_parse,
                cb_kwargs={'user_id': user_id,
                           'username': username,
                           'variables': deepcopy(variables)}
            )

        subscriptions = j_data.get('data').get('user').get('edge_follow').get('edges')
        for subscription in subscriptions:
            item = InstaparserItem(
                user_id=user_id,
                user_name=username,
                subscriber_id=subscription['node']['id'],
                subscriber_name=subscription['node']['username'],
                subscriber_fullname=subscription['node']['full_name'],
                photo=subscription['node']['profile_pic_url'],
                subscriber_type='subscription'
            )
            yield item


    def fetch_csrf_token(self, text):
        ''' Get csrf-token for auth '''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
