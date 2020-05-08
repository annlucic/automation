Чтобы запустить дашборд, необходимо выполнить следующие шаги:


1. Установить PostgreSQL


В командной строке/терминале вызвать команды


sudo apt update 
sudo apt install postgresql postgresql-contrib 


sudo service postgresql start
service postgresql status  #результат - 'online'


2. Создать базу данных на той машине, где будет запускаться дашборд:


 createdb zen —encoding='utf-8'


3. Войти в консоль PostgreSQL и выполните команды:


\c zen
CREATE USER my_user WITH ENCRYPTED PASSWORD 'my_user_password';
\q


4. Загрузите в базу данных данные из бэкап-файла:


pg_restore -d zen zen_copy.dump


5. Установить пакетный менеджер python и библиотеки


Linux и Ubuntu


sudo apt install python3-pip
sudo pip3 install dash==1.6.1
sudo pip3 install sqlalchemy
sudo apt-get install python3-psycopg2
sudo pip3 install pandas


Windows 7


python -m pip install dash==1.6.1
python -m pip install sqlalchemy
python -m pip install psycopg2
python -m pip install pandas




6. Если запуск производится на виртуальной машине, необходимо сначала скопировать файл на нее файлы zen_pipeline.py и zen_dash.py командой scp:


scp <путь к файлу на локальной машине>  <логин виртуальной машины>@<публичный IP>:


7. Вызвать скрипт пайплайна


На локальной машине в командной строке перейдите в папку, где вы сохранили файл


Linux или Ubuntu
python3 zen_pipeline.py


А в Windows или MacOS:
python zen_pipeline.py.py


8. Вызвать скрипт дашборда


python3  zen_dash.py


9. В браузере ввести


На локальной машине: <публичный_IP-адрес_виртуальной машины>:3000


На локальной машине: <локальный_IP-адрес>:3000


10. Как в случае локального запуска, так и на виртуальной машине дашборд «захватывает» текущее окно терминала командной строки и не даст возможности выполнять другие команды. Чтобы остановить программу дашборда, нажмите Ctrl+C. Ваш дашборд остановится и больше не будет виден по публичному IP-адресу.