#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查下载的图片是否正确
"""

import os
from PIL import Image
import requests

def check_image_info(image_path):
    """检查图片信息"""
    try:
        with Image.open(image_path) as img:
            print(f"图片: {image_path}")
            print(f"  尺寸: {img.size}")
            print(f"  格式: {img.format}")
            print(f"  模式: {img.mode}")
            print(f"  文件大小: {os.path.getsize(image_path)} bytes")
            print()
    except Exception as e:
        print(f"无法打开图片 {image_path}: {e}")

def test_url_accessibility(url):
    """测试URL是否可访问"""
    try:
        response = requests.head(url, timeout=10)
        print(f"URL: {url}")
        print(f"  状态码: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        print(f"  Content-Length: {response.headers.get('Content-Length', 'Unknown')}")
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"URL访问失败 {url}: {e}")
        return False

def main():
    print("检查《活着》封面图片")
    print("=" * 50)
    
    # 检查本地图片
    image_dir = "covers/活着"
    if os.path.exists(image_dir):
        print("本地图片信息:")
        for filename in ['small.jpg', 'medium.jpg', 'large.jpg']:
            image_path = os.path.join(image_dir, filename)
            if os.path.exists(image_path):
                check_image_info(image_path)
    
    # 测试URL可访问性
    print("URL可访问性测试:")
    urls = [
        "https://img9.doubanio.com/view/subject/s/public/s29053580.jpg",
        "https://img9.doubanio.com/view/subject/m/public/s29053580.jpg", 
        "https://img9.doubanio.com/view/subject/l/public/s29053580.jpg"
    ]
    
    for url in urls:
        test_url_accessibility(url)

if __name__ == "__main__":
    main()


