# Apache2 Dockerfile for Tennis Team Website
FROM httpd:2.4-alpine

# Install additional dependencies
RUN apk add --no-cache \
    openssl \
    mod_ssl \
    mod_wsgi \
    && rm -rf /var/cache/apk/*

# Enable required Apache modules
RUN sed -i '/LoadModule mpm_event_module/d' /usr/local/apache2/conf/httpd.conf
RUN sed -i '/LoadModule mpm_worker_module/d' /usr/local/apache2/conf/httpd.conf
RUN echo "LoadModule mpm_prefork_module modules/mod_mpm_prefork.so" >> /usr/local/apache2/conf/httpd.conf
RUN echo "LoadModule wsgi_module modules/mod_wsgi.so" >> /usr/local/apache2/conf/httpd.conf

# Create directories
RUN mkdir -p /var/www/html
RUN mkdir -p /var/www/static
RUN mkdir -p /etc/apache2/ssl
RUN mkdir -p /etc/apache2/sites-enabled
RUN mkdir -p /var/log/apache2

# Copy configuration
COPY docker/apache/tennis.conf /etc/apache2/sites-enabled/tennis.conf

# Set permissions
RUN chown -R www-data:www-data /var/www
RUN chmod -R 755 /var/www

# Expose ports
EXPOSE 80 443

# Start Apache
CMD ["httpd", "-D", "FOREGROUND"]