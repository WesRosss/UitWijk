# Vue.js Frontend Dockerfile for Tennis Team Website
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install dependencies
COPY frontend/package*.json /app/
RUN npm install

# Copy source code
COPY frontend/ /app/

# Build the application
RUN npm run build

# Expose port
EXPOSE 8080

# Command to run the development server
CMD ["npm", "run", "serve"]

# For production, use nginx to serve the built files
# FROM nginx:alpine
# COPY --from=builder /app/dist /usr/share/nginx/html
# COPY nginx.conf /etc/nginx/conf.d/default.conf
# EXPOSE 80
# CMD ["nginx", "-g", "daemon off;"]