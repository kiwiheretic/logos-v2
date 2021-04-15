#!/bin/sh
if [ ! -f sqlite-databases/bibles.sqlite3.db ]; then
  ln -s /mnt/bibles/bibles.sqlite3.db sqlite-databases/bibles.sqlite3.db ;
fi
python3 manage.py run_bot -s "${SERVER:-irc.chatopia.net}" --botname ${NICK:-defaultnick3726} --rooms ${ROOMS:-"#bottest"}
