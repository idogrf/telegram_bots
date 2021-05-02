FROM python:3.9.1

# Create directory
ENV APP_DIRECTORY '/app'
RUN mkdir -p ${APP_DIRECTORY}

#RUN apt install gcc

# Install python requirements
COPY requirements.txt /app
RUN pip3 install -r ${APP_DIRECTORY}/requirements.txt

# Copy contents of directory
COPY . /app

#CMD [ "python3", "${APP_DIRECTORY}/telegram_bot_service.py" ]