FROM python:3.9-slim
ENV BOT_TOKEN="6729587033:AAExZVf5nYVmDwa81WIWH3bz6T1uOQugLpY"
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN mkdir /app/post_tmp
CMD ["python", "main.py"]