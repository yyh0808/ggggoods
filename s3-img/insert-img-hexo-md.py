#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import re

# 设置路径
CSV_FILE_PATH = 'image_urls.csv'  # CSV 文件路径
POSTS_DIR = '../source/_posts'  # Hexo posts 目录路径

# 读取 CSV 文件并建立关键词映射
def read_csv(file_path):
    keyword_to_url = {}
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            filename = row['Local File Name']
            url = row['R2 URL']

            # 从文件名中提取关键词
            # 文件名格式: "Surreal,science fiction,关键词,English,technology,tech,diagrams,renderings,colors_20240830_00001_.png"
            parts = filename.split(',')
            if len(parts) >= 3:
                # 第三个部分通常是中文关键词
                keyword = parts[2].strip()
                keyword_to_url[keyword] = url
                print(f"映射关键词: {keyword} -> {url}")

    return keyword_to_url

# 更新 Markdown 文件的 cover 字段
def update_markdown_file(file_path, image_url):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 检查是否已有cover字段
    if re.search(r'^cover:\s*', content, re.MULTILINE):
        # 替换现有的cover字段
        updated_content = re.sub(r'^cover:\s*.*$', f'cover: {image_url}', content, flags=re.MULTILINE)
    else:
        # 在front matter中添加cover字段
        # 找到第二个---之前的位置
        parts = content.split('---', 2)
        if len(parts) >= 3:
            front_matter = parts[1]
            rest = parts[2]
            front_matter += f'\ncover: {image_url}\n'
            updated_content = '---' + front_matter + '---' + rest
        else:
            print(f"无法解析front matter: {file_path}")
            return False

    # 写回文件
    if updated_content != content:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        return True
    else:
        return False

# 主函数
def main():
    print("开始处理文章封面图...")

    # 读取CSV映射
    keyword_to_url = read_csv(CSV_FILE_PATH)
    print(f"读取到 {len(keyword_to_url)} 个图片映射")

    # 获取所有markdown文件
    if not os.path.exists(POSTS_DIR):
        print(f"错误: 文章目录不存在: {POSTS_DIR}")
        return

    updated_count = 0
    not_found_count = 0

    for filename in os.listdir(POSTS_DIR):
        if filename.endswith('.md'):
            # 从文件名提取关键词（去掉.md扩展名）
            keyword = os.path.splitext(filename)[0]

            if keyword in keyword_to_url:
                image_url = keyword_to_url[keyword]
                markdown_path = os.path.join(POSTS_DIR, filename)

                if update_markdown_file(markdown_path, image_url):
                    print(f"✓ 更新 {keyword}: {image_url}")
                    updated_count += 1
                else:
                    print(f"- 跳过 {keyword}: 内容未变化")
            else:
                print(f"✗ 未找到匹配的图片: {keyword}")
                not_found_count += 1

    print(f"\n更新完成:")
    print(f"成功更新: {updated_count} 个文件")
    print(f"未找到匹配: {not_found_count} 个文件")

if __name__ == "__main__":
    main()