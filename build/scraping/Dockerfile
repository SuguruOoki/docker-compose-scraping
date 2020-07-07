FROM python:3.8.3-alpine3.12

WORKDIR /var/lib/python3

# COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip
# NOTE
# 依存関係を勝手にrequiments.txtで解決してくれず、
# アルファベット順にインストールされるため、先にnumpyをinstallする。
RUN pip install pipenv
RUN pipenv lock --clear
RUN pipenv install

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
