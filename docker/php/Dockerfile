FROM php:8.0-fpm
COPY php.ini /usr/local/etc/php/

# RUN apt-get update \
#   && apt-get install -y zlib1g-dev mariadb-client vim libzip-dev \
#   && docker-php-ext-install zip pdo_mysql

# #Composer install
# RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
# RUN php composer-setup.php
# RUN php -r "unlink('composer-setup.php');"
# RUN mv composer.phar /usr/local/bin/composer

# ENV COMPOSER_ALLOW_SUPERUSER 1

# ENV COMPOSER_HOME /composer

# ENV PATH $PATH:/composer/vendor/bin


# WORKDIR /var/www

# RUN composer global require "laravel/installer"

COPY php.ini /usr/local/etc/php/

# Composer install
COPY --from=composer:2.5.1 /usr/bin/composer /usr/bin/composer

# install Node.js
COPY --from=node:19.5.0 /usr/local/bin /usr/local/bin
COPY --from=node:19.5.0 /usr/local/lib /usr/local/lib

RUN apt-get update && \
    apt-get -y install \
    git \
    zip \
    unzip \
    vim \
    && docker-php-ext-install pdo_mysql bcmath

WORKDIR /var/www/twistats