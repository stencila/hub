FROM nginx

COPY nginx.conf /etc/nginx/conf.d/default.conf.template
COPY 50x.html /usr/share/nginx/html/
COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
