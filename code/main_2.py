from collector import Collector
from threading import Thread

def input_data():
  api_token_vk = input("Введите свой token пользователя vk: ")

  openAI_api_key = input("Введите свой openAI_api_key: ")
  
  return api_token_vk, openAI_api_key

def main(collector_vk: Collector):
  
  while len(collector_vk.all_posts) < 20000 or len(collector_vk.all_comments) < 40000:
    collector_vk.logger.log_to_console("Начало отбора постов...", "info")
    collector_vk.collect_posts(group_count=100, posts_group_count=100)

    collector_vk.logger.log_to_console("Начало отбора коментариев...", 'info')
    collector_vk.collect_comments(collector_vk.all_posts[collector_vk.filtered_posts_for_comments:])


api_token_vk, openAI_api_key = input_data()

collector_vk = Collector(api_token_vk=api_token_vk, openai_api_key=openAI_api_key)

main(collector_vk)

collector_vk.write_to_csv(collector_vk.all_posts)
collector_vk.write_to_csv(collector_vk.all_comments, 'comments')

collector_vk.logger.log_to_console("Данные собраны и записаны!", 'info')
