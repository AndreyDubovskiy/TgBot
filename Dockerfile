FROM python:3.9-slim
ENV BOT_TOKEN="6729587033:AAESDJSwGSgA8zxfLLEW1sOvg6HPF68LzB4"
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN mkdir /app/post_tmp
CMD ["python", "main.py"]