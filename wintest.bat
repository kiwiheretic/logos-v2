rem * winrun.bat
call ..\venvs\logos-v2\Scripts\activate
python manage.py run_biblebot -s irc.cornerstonechristianchat.com --port=6668 ^
  -n Logos_test --engine-room="#logos-testing" -P zxcvbnm %*