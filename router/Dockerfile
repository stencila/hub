FROM nginx

COPY nginx.conf /etc/nginx/conf.d/default.conf.template
COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
