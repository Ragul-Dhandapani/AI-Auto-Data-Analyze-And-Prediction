#!/bin/bash

# Quick script to switch from MongoDB to Oracle

echo "Switching to Oracle database..."

# Update .env file
sed -i 's/DB_TYPE="mongodb"/DB_TYPE="oracle"/' /app/backend/.env

echo "✅ Updated DB_TYPE to oracle"

# Restart backend
sudo supervisorctl restart backend

echo "✅ Backend restarting..."
sleep 5

# Test connection
curl -s http://localhost:8001/api/datasets > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Successfully switched to Oracle!"
else
    echo "❌ Oracle connection failed. Check logs:"
    echo "  tail -n 50 /var/log/supervisor/backend.err.log"
fi
