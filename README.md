# Автоматизация в Яндекс.Дзене

**Описание проекта:** В проекте моделируется ситуация, когда необходимо автоматизировать процесс и сделать дашборд. Дашборд позволит автоматизировать регулярную задачу и упростить менеджерам процесс получения данных по взаимодействию пользователей с карточками статей.

**Данные:** бэкап-файл с базы данных PostgreSQL (на период проектирования и тестирования, администраторы БД выделили тестовую базу zen, создали там таблицу log_raw и выгрузили в неё 322 391 записей из основной таблицы логов)

Каждую карточку определяют её тема и источник. Пользователей системы характеризует возрастная категория. Есть три способа взаимодействия пользователей с системой: отображение карточки (show), клик (click), просмотр (view).

В таблице log_raw:

сохранены события за 60 минут;
всего 6 возрастных групп;
встречаются события 3 типов;
есть 25 тем карточек и 26 тем источников.
Проект Яндекс.Практикума

**Задача:** Сделать дашборд, позволяющий ответить на вопросы:

Сколько взаимодействий пользователей с карточками происходит в системе с разбивкой по темам карточек?
Как много карточек генерируют источники с разными темами?
Насколько хорошо пользователи конвертируются из показов карточек в просмотры статей?

**Техническое задание**
Совместно с менеджерами и администраторами баз данных, составлено краткое ТЗ:

1. Бизнес-задача: анализ взаимодействия пользователей с карточками Яндекс.Дзен;
2. Насколько часто предполагается пользоваться дашбордом: не реже, чем раз в неделю;
3. Кто будет основным пользователем дашборда: менеджеры по анализу контента;
4. Состав данных для дашборда:
    - История событий по темам карточек;
    - Разбивка событий по темам источников;
    - Глубина взаимодействия пользователей с карточками (воронка: показ — клик — просмотр);
5. По каким параметрам данные должны группироваться:
    - Дата и время;
    - Тема карточки;
    - Тема источника;
    - Возрастная группа;
    - Тип события;
6. Характер данных:
    - История событий по темам карточек — абсолютные величины с разбивкой по минутам;
    - Разбивка событий по темам источников — относительные величины (% событий);
    - Глубина взаимодействия пользователей с карточками — относительные величины (средний % от показов);
7. Важность: график истории событий по темам карточек важнее всего, он должен занимать не меньше половины площади дашборда;
8. Источники данных для дашборда: cырые данные о событиях взаимодействия пользователей с карточками (таблица log_raw);
9. База данных, в которой будут храниться агрегированные данные: дополнительные агрегированные таблицы в БД zen;
10. Частота обновления данных: один раз в сутки, в полночь по UTC;
11. Какие графики должны отображаться и в каком порядке, какие элементы управления должны быть на дашборде (макет дашборда).

**На основании ТЗ на дашборде нужно отобразить:**

- Историю событий по минутам с разбивкой по темам карточек;
- Разбивку всех событий по темам источников;
- Усреднённую воронку: уникальные показы -> уникальные клики -> уникальные просмотры.

Кроме того, понадобится обеспечить фильтрацию по времени, темам карточек и возрастным группам.

### 1. Подготовка данных

- Создана виртуальная машина в Яндекс.Облаке 
- Установлена PostgreSQL 
- Развернута база данных из dump-файла
- Установлен пакетный менеджер и библиотеки


### 2. Создание аггрегирующих таблиц

В базе данных создано две аггрегирующие таблицы.
1. Таблица воронки просмотров 
```SQL
CREATE TABLE dash_engagement(record_id serial PRIMARY KEY, 
                             dt TIMESTAMP,        
                             item_topic VARCHAR(128),     
                             event VARCHAR(128),    
                             age_segment VARCHAR(128),
                             unique_users BIGINT);
```                     
2. Таблица истории событий

```SQL
CREATE TABLE dash_visits(record_id serial PRIMARY KEY,       
                         item_topic VARCHAR(128),
                         source_topic VARCHAR(128),
                         age_segment VARCHAR(128),
                         dt TIMESTAMP,
                         visits INT);
```  
### 4. Пайплайн 

1. Заданы входные параметры пайплайна: `start_dt` и `end_dt`
2. Задано подключение к БД 
3. Задана группировка для датафреймов событий и воронок в соответствии с определениями их таблиц.
4. Добавлено удаление ранее записанных данных и запись новых данных.
5. Вызван скрипт пайплайна для всего диапазона тестовых данных

### 5. Дашборд

1. Заданы данные для отрисовки
2. Получены сырые данные из базы
3. Задан лейаут
4. Сформирован html
5. Отрисованы три графика
6. Описана логика дашборда
7. Применена фильтрация
8. Сформирован результат отображения

*ИНСТРУКЦИЯ ПО ЗАПУСКУ СКРИПТА ПАЙПЛАЙНА И ДАШБОРДА В ФАЙЛЕ readme.txt*

Порядок элементов управления:

1. График событий во времени
2. Круговая диаграмма событий
3. Столбчатая диаграмма глубины взаимодействия

<img src="dash_screen2.png?raw=true"/>

### 6. Используемые инструменты

Библиотеки python - dash, pandas, sqlalchemy, psycopg2

Виртуальная машина в Яндекс.Облаке(ubuntu)

PostgreSQL 

