#!/bin/bash

# Cloudflare Pages Build Script for Hexo
echo "Starting Hexo build process..."

# Install dependencies
echo "Installing dependencies..."
npm install

# Clean previous build
echo "Cleaning previous build..."
npm run clean

# Generate static files
echo "Generating static files..."
npm run build

echo "Build completed successfully!"
echo "Output directory: public"
