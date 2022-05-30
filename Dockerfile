FROM python:3.8-slim-bullseye
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

#RUN python setup.py build_ext --inplace

EXPOSE 80
RUN mkdir ~/.streamlit
RUN cp .streamlit/config.toml ~/.streamlit/config.toml
RUN cp .streamlit/credentials.toml ~/.streamlit/credentials.toml
WORKDIR /app

# ssh
ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
        && apt-get install -y --no-install-recommends dialog \
        && apt-get update \
	&& apt-get install -y --no-install-recommends openssh-server \
	&& echo "$SSH_PASSWD" | chpasswd

COPY sshd_config /etc/ssh/
EXPOSE 8000 2222

#ENTRYPOINT ["streamlit", "run"]
#CMD ["app.py"]
COPY init.sh /usr/local/bin/
RUN chmod u+x /usr/local/bin/init.sh
ENTRYPOINT ["init.sh"]