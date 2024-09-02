FROM ubuntu:focal 

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y siege 
RUN mkdir /smoke
COPY request-script.sh /smoke
COPY entrypoint.sh /usr/bin/entrypoint.sh
RUN chmod 755 /smoke/request-script.sh && \
    chmod 755 /usr/bin/entrypoint.sh
ENTRYPOINT ["/usr/bin/entrypoint.sh"]
CMD ["/smoke/request-script.sh"]
