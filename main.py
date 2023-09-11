from collector import Collector
from threading import Thread

def input_data():
  api_token_vk = input("Введите свой token пользователя vk: ")

  openAI_api_key = input("Введите свой openAI_api_key: ")
  
  return api_token_vk, openAI_api_key

def main(collector_vk: Collector):
  filtering_posts = None
  filtering_comments = None

  while len(collector_vk.filter.all_filtered_posts) < 60 or len(collector_vk.filter.all_filtered_comments) < 70:
    collector_vk.logger.log_to_console("Начало отбора постов...", "info")
    collector_vk.collect_posts()

    if filtering_posts != None:
      collector_vk.logger.log_to_console("Ожидание окончания фильтрации постов...", "info")
      filtering_posts.join()

    if filtering_comments != None:
      collector_vk.logger.log_to_console("Ожидание окончания фильтрации комментариев...", 'info')
      filtering_comments.join()
      filtering_comments = None

    collector_vk.logger.log_to_console("Начало фильтрации постов...", 'info')
    filtering_posts = Thread(target=collector_vk.filter.full_filtering, args=[collector_vk.all_posts])
    filtering_posts.start()

    collector_vk.all_posts = []

    if len(collector_vk.filter.all_filtered_posts) - collector_vk.filtered_posts_for_comments > 30:

      collector_vk.logger.log_to_console("Начало отбора коментариев...", 'info')
      collector_vk.collect_comments(collector_vk.filter.all_filtered_posts[collector_vk.filtered_posts_for_comments:])

      filtering_posts.join()
      filtering_posts = None

      collector_vk.logger.log_to_console("Начало фильтрации коментариев...", 'info')
      filtering_comments = Thread(target=collector_vk.filter.full_filtering, args=[collector_vk.all_comments, 'comments'])
      filtering_comments.start()

      collector_vk.all_comments = []

  return filtering_posts, filtering_comments
    
if __name__ == "__main__":

  api_token_vk, openAI_api_key = input_data()

  collector_vk = Collector(api_token_vk=api_token_vk, openai_api_key=openAI_api_key)

  filtering_posts, filtering_comments = main(collector_vk)

  if filtering_posts != None:
    collector_vk.logger.log_to_console("Ожидание окончания фильтрации постов...", "info")
    filtering_posts.join()

  if filtering_comments != None:
    collector_vk.logger.log_to_console("Ожидание окончания фильтрации комментариев...", 'info')
    filtering_comments.join()

  collector_vk.write_to_csv(collector_vk.filter.all_filtered_posts)
  collector_vk.write_to_csv(collector_vk.filter.all_filtered_comments, 'comments')

  collector_vk.logger.log_to_console("Данные собраны и записаны!", 'info')