from datetime import datetime
import pytz
import vk_api
import csv
import re
from Filter import Filter
from log import Logging

class Collector(object):
    
    def __init__(self, api_token_vk: str, openai_api_key: str) -> None:
        self.vk_session = vk_api.VkApi(token=api_token_vk)
        self.all_posts, self.all_comments = [], []
        self.logger = Logging()
        self.filter = Filter(openai_api_key, self.logger)
        self.offset_posts = 0
        self.offset_groups = 0
        self.filtered_posts_for_comments = 0
        

    def collect_posts(self, theme='Футбол', group_count=100, posts_group_count=2) -> None:

        groups = self.collect_groups(theme, group_count)
        all_posts_in_groups = 0

        for group in groups['items']:
            try:
                posts_request = self.vk_api_request('wall.get', {'domain': group['screen_name'], 'count': posts_group_count, 'offset': self.offset_posts})

                all_posts_in_groups += len(posts_request['items'])

                for post in posts_request['items']:
                    ners = self.filter.basic_filtering_posts(post)
                    if not ners:
                        continue
                    post_formatted = self.formatting_posts(post, group['screen_name'], ners)
                    self.all_posts.append(post_formatted)

            except vk_api.exceptions.ApiError:
                continue

        if all_posts_in_groups == 0:
                self.offset_posts = 0
                self.offset_groups += 100
        else:
            self.offset_posts += posts_group_count

    def collect_comments(self, all_posts: list) -> None:
        for post in all_posts:
            try:
                response = self.vk_api_request('wall.getComments', {'owner_id': post['owner_id'], 'post_id': post['id']})
                
                for comment in response['items']:
                    ners = self.filter.basic_filtering_comments(comment, post)
                    if not ners:
                        continue

                    post_comment = self.formatting_comments(comment, ners)
                    self.all_comments.append(post_comment)

            except vk_api.exceptions.ApiError:
                continue
        
        self.filtered_posts_for_comments += len(all_posts)

    def collect_groups(self, theme='Футбол', group_count=100) -> dict:
        return self.vk_api_request('groups.search', values={'q': theme, 'type': 'group', 'country_id': 1, 'count': group_count, 'offset': self.offset_groups})
    
    def formatting_posts(self, post: dict, group_name: str, ners: set) -> dict:
        group_post = {}

        group_post['id'] = post['id']
        group_post['text'] = post['text'].replace('\n', '. ')
        group_post['group_link'] = f'https://vk.com/{group_name}' 
        group_post['date'] = datetime.fromtimestamp(post['date'], tz=pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')
        group_post['ners'] = ners
        group_post['ners_num'] = len(ners)
        group_post['words_num'] = len(re.findall(r'[a-zа-яё]+', post['text'], flags=re.IGNORECASE))
        group_post['comments_num'] = post['comments']['count']
        group_post['owner_id'] = post['owner_id']
        
        return group_post
    
    def formatting_comments(self, comment: dict, ners: set) -> dict:
        post_comment = {}

        post_comment['id'] = comment['id']
        post_comment['text'] = comment['text'].replace('\n', '. ')
        post_comment['post_id'] = comment['post_id']
        post_comment['date'] = datetime.fromtimestamp(comment['date'], tz=pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S')
        post_comment['ners'] = ners
        post_comment['ners_num'] = len(ners)
        post_comment['words_num'] = len(re.findall(r'[a-zа-яё]+', comment['text'], flags=re.IGNORECASE))

        return post_comment
    
    def write_to_csv(self, data: list, type_data = 'posts') -> None:
        self.logger.log_to_console(f"Начало записи {type_data} в csv...", 'info')
        if type_data != 'posts' and type_data != 'comments':
            self.logger.log_to_console("Введенный тип данных неподдерживается. Проверьте данные!", 'error')
            return

        fieldnames = list(data[0].keys())
        if type_data == 'posts':
            fieldnames.remove('owner_id')

        with open(f"result/filtered_{type_data}.csv", "a+", encoding='utf-8-sig') as file:
            file_writer = csv.DictWriter(file, delimiter = ";", lineterminator="\n", fieldnames=fieldnames)

            file_writer.writeheader()
            for value in data:
                try:
                    if type_data == 'posts':
                            value.pop('owner_id')
                    file_writer.writerow(value)
                except Exception:
                    continue
    
    def vk_api_request(self, method: str, values: dict) -> dict:
        return self.vk_session.method(method, values)
