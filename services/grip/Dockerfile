# Ubuntu Long Term Release
FROM ubuntu:22.04

# Use bash instead of sh
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Update the package manager database
RUN apt-get update -y

# Need curl to install Node
RUN apt-get install -y curl

# Copy over code. Make sure to exclude
# unwanted things in .dockerignore
COPY frontend frontend

# Move into project directory 
WORKDIR frontend

# Install the Node version manager and Node.
# The default Node for this version of Ubuntu is incompatible
# with the Vite build system.
# Also run the node install and vite build.
RUN mkdir /usr/local/nvm
ENV NVM_DIR /usr/local/nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash \
    && . $NVM_DIR/nvm.sh \
    && nvm install v16.13.0 \
    && npm ci \
    && npm run build

# Install Nginx
RUN apt-get install nginx -y

# Link nginx to the project directory
RUN rm -rf /var/www/html
RUN ln -s /frontend/dist /var/www/html

# Expose the http port
EXPOSE 80:80

# Run the web server
CMD ["/usr/sbin/nginx", "-g", "daemon off;"]