# ==============================================================================
# Sential Intelligence Platform - Frontend Dockerfile
# Production multi-stage build: Vite compilation + Nginx static serving & reverse proxy
# ==============================================================================

# Stage 1: Build production static bundle
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies using reproducible lockfile
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code and build assets
COPY . .

# Set default relative API endpoint for Nginx reverse-proxy
ENV VITE_API_URL=/api/v1
RUN npm run build

# Stage 2: Production Nginx web server
FROM nginx:1.25-alpine

# Install curl for container health check
RUN apk add --no-cache curl

# Remove default static files and config
RUN rm -rf /etc/nginx/conf.d/default.conf /usr/share/nginx/html/*

# Copy compiled static assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration (reverse-proxy + SPA fallback)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port
EXPOSE 80

# Health check
HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
