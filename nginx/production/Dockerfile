FROM nginx:1.21-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d

COPY /data/certs/moderation_ssl_crt /etc/nginx/certs/
COPY /data/certs/moderation_ssl_key /etc/nginx/certs/

COPY /data/.htpasswd /etc/nginx/

RUN mkdir -p etc/nginx/logs
