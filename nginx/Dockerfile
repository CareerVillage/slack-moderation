FROM nginx:1.31.3-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d

RUN mkdir -p etc/nginx/logs
