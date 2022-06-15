# Ubuntu Long Term Release
FROM ubuntu:22.04

# Update the package manager database
RUN apt-get update -y

# Install Nginx
RUN apt-get install nginx -y

# Expose the http port
EXPOSE 80:80

# Run the web server
CMD ["/usr/sbin/nginx", "-g", "daemon off;"]