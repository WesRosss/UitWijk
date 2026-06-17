# Vue.js Frontend Dockerfile for Tennis Team Website
# Optimized for use with external Apache2 reverse proxy
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install dependencies
COPY frontend/package*.json /app/
RUN npm install

# Copy source code
COPY frontend/ /app/

# Expose port for development
EXPOSE 8080

# Command to run the development server on port 8081
CMD ["npm", "run", "serve", "--", "--port", "8081"]