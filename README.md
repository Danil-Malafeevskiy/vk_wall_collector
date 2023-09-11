# vk_wall_collector
Сборщик записей VK из групп на заданную тематику. Сборщик производит сбор постов из групп и отдает их фильтратору на базовую фильтрацию, которая включает в себя проверку на количество слов в тексте поста, количество коментариев под постом, а также поиск именованных сущностей. 

В сборщике также присутствует отбор комментариев и их фильтрация. 
 
В фильтраторе есть метод полной фильтрации, который использует OpenAI для отбора текста без грамматических ошибок, без рекламы и спама и относящихся к теме футбол (или заданной). Запросы OpenAI заделаются в отдельном потоке.

В первом файле main реализована полная работа программы. Сбор постов и комментариев и их полная фильтрация с использованием AI. Фильтрация производится в отдельных потоках. 

Во втором файле main_2 реализован базовый сборщик без фильтрации по OpenAI. 

# Зависимости
  - pip install pytz,
  - pip install vk_api,
  - pip install spacy,
  - pip install openai,
  - spacy download ru_core_news_lg

# Структура
1. Класс сборщика постов и комментариев Collector, со встроенным фильтратором (Collector.py). 
2. Класс фильтрации постов и комментариев Filter (Filter.py).
3. Класс логирования Logging, выводящий логи в консоль (Log.py).
4. 2 main файла. Которые выполняют задачу по-разному (main.py и main_2.py).
