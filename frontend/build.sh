#!/usr/bin/env bash
# Build script for Render.com frontend

echo "Building frontend..."
npm install
npm run build

echo "Setting up SPA routing..."
# Render.com specific: ensure all routes serve index.html
echo '/*    /index.html   200' > dist/_redirects

echo "Build complete!"
ls -la dist/
