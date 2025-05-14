#!/bin/bash
# start.sh

# Tạo thư mục cần thiết
mkdir -p models uploads results latents

# Tải mô hình (nếu chưa có)
cd backend
python download_models.py
cd ..

# Khởi động Nginx
service nginx start

# Khởi động Flask API
cd backend
python app.py