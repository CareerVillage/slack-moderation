FROM nginx:1.19.0-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY ${CONFIG_FILE} /etc/nginx/conf.d
