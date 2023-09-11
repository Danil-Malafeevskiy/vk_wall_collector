from ast import literal_eval
from time import sleep
import spacy
import re
import openai
from multiprocessing.pool import ThreadPool
from log import Logging

class Filter(object):
    
    def __init__(self, openai_api_key: str, logger: Logging) -> None:
        openai.api_key = openai_api_key
        self.model_engine = "gpt-3.5-turbo"
        self.nlp = spacy.load("ru_core_news_lg")
        self.all_filtered_posts, self.all_filtered_comments = [], []
        self.logger = logger

    def basic_filtering_posts(self, post: dict):
        if len(re.findall(r'[a-zа-яё]+', post['text'], flags=re.IGNORECASE)) <= 10  or post['comments']['count'] <= 1 or len(post['text']) > 3000:
            return False    

        no_emoji_pattern = re.compile("["
                u"\U0001F600-\U0001F64F"
                u"\U0001F300-\U0001F5FF"
                u"\U0001F680-\U0001F6FF"
                u"\U0001F1E0-\U0001F1FF"
                u"\U00002702-\U000027B0"
                u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
        
        doc = self.nlp(no_emoji_pattern.sub(r'', post['text']))

        for entity in doc.ents:
            entity_res = entity.text
            if entity_res.endswith(' "'):
                entity_res = entity_res.replace(' "', '')

        named_entities = set(doc.ents)
        return named_entities

    def basic_filtering_comments(self, comment: dict, post: dict):
        if len(re.findall(r'[a-zа-яё]+', comment['text'], flags=re.IGNORECASE)) < 4 or len(comment['text']) > 3000:
            return False

        no_emoji_pattern = re.compile("["
                u"\U0001F600-\U0001F64F"
                u"\U0001F300-\U0001F5FF"
                u"\U0001F680-\U0001F6FF"
                u"\U0001F1E0-\U0001F1FF" 
                u"\U00002702-\U000027B0"
                u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)

        doc = self.nlp(no_emoji_pattern.sub(r'', comment['text']))

        named_entities = set(doc.ents)

        '''if not len(set.intersection(named_entities, post['ners'])):
            return False'''
        
        return named_entities
    
    def full_filtering(self, all_data: list, type_data='posts') -> None:
        if type_data != 'posts' and type_data != 'comments':
            self.logger.log_to_console("Введенный тип данных неподдерживается. Проверьте данные!", 'error') 
            return
        
        index = 0
        while index != len(all_data):
            prompt_data = []
            prompt_lenght = 0
            start_index_prompt = index
            while prompt_lenght + len(all_data[index]['text']) <= 3000:
                prompt_data.append(all_data[index]['text'].replace('«', '').replace('»', '').replace('"', '').replace("'", ''))
                prompt_lenght += (len(all_data[index]['text']) + 2)

                index += 1
                if len(all_data) == index or len(prompt_data) == 10:
                    break
            
            if type_data == 'comments':
                print(prompt_data)
                print()

            while True:
                try:
                    prompt = f"{prompt_data} - тебе дан массив строк. Пройдись по по всем строкам в нем и создай свой массив из логических значений 1 и 0. Если текст относится к теме футбол, и в нем нет грамматических ошибок, и в тексте нет рекламы и спама, то добавь в массив результата 1, иначе - 0, если не уверен поставь 0. Ответь только массивом результатов без пояснений."

                    pool = ThreadPool(processes=1)

                    async_result = pool.apply_async(openai.ChatCompletion.create, kwds={'model': self.model_engine, 'messages': [{'role': 'user', 'content': prompt}]})

                    answer = async_result.get().choices[0].message.content

                    res_start_index = answer.find('[')
                    res_end_index = answer.rfind(']')
                    results = literal_eval(answer[res_start_index:res_end_index+1])

                    if len(results) > len(prompt_data):
                        results = results[:len(prompt_data)]
                    
                    if len(results) < len(prompt_data):
                        index -= (len(prompt_data) - len(results))

                    for result in results:
                        if result:
                            if type_data == 'posts':
                                self.all_filtered_posts.append(all_data[start_index_prompt])
                            else:
                                self.all_filtered_comments.append(all_data[start_index_prompt])
                        start_index_prompt += 1
                    
                    sleep(20)
                    prompt_data.clear()
                    prompt_lenght = 0
                    break

                except Exception:
                    self.logger.log_to_console("Слишком много запросов к OpenAI! Wait 20 sec...", 'error') 
                    sleep(20)
