# Invoke with: docker build -t kiwiheretic/logos3:v0.1 -f  Dockerfile scripts/
FROM kiwiheretic/pybase:v0.1
MAINTAINER kiwiheretic@myself.com
RUN adduser -h /home/logos -u 1000 -D logos
USER logos
WORKDIR /home/logos
RUN git clone --branch python3 https://github.com/kiwiheretic/logos-v2.git ~/logos3
WORKDIR /home/logos/logos3
RUN pip install -r requirements.txt
#  && ln -s /mnt/bibles/bibles.sqlite3.db sqlite-databases/bibles.sqlite3.db
RUN ( rm irctk || true ) && ( rm -fr vendor/irctk || true ) \
  && git clone https://github.com/kylef/irctk.git vendor/irctk \
  && touch vendor/irctk/__init_.py \
  && ln -s vendor/irctk/irctk irctk
COPY --chown=logos run.sh .
RUN chmod +x run.sh
RUN cp -f logos/email_settings-dist.py logos/email_settings.py 
RUN cp -f allowed_hosts-dist.txt allowed_hosts.txt 
RUN echo "SECRET_KEY = 'ijpvj-lzq3%su2u-q3x0aiw1c-8qlchds=4acd'" >> logos/settings.py
RUN python3 manage.py migrate
ENTRYPOINT /home/logos/logos3/run.sh
