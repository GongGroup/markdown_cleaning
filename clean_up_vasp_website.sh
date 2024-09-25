#!/bin/bash

# 定义目标目录和日志文件
TARGET_DIR="/Users/mastreina/Desktop/vasp_wiki_html_240912"
LOG_FILE="/Users/mastreina/Desktop/deleted_files.log"

# 清空日志文件（如果存在）
> "$LOG_FILE"

# 递归遍历目录并删除以 "talk_", "file_", "Construction_", "MediaWiki_", "Special_" (大小写不敏感) 开头的文件
find "$TARGET_DIR" -type f \( -iname "talk_*" -o -iname "file_*" -o -iname "construction_*" -o -iname "mediawiki_*" -o -iname "special_*" \) -exec rm -v {} \; | tee -a "$LOG_FILE"

# 删除所有不是 .html 格式的文件，并记录到日志中
find "$TARGET_DIR" -type f ! -iname "*.html" -exec rm -v {} \; | tee -a "$LOG_FILE"

# 递归遍历目录并删除以 "talk_", "file_", "Construction_", "MediaWiki_", "Special_" (大小写不敏感) 开头的文件夹
find "$TARGET_DIR" -type d \( -iname "talk_*" -o -iname "file_*" -o -iname "construction_*" -o -iname "mediawiki_*" -o -iname "special_*" \) -exec rm -rv {} \; | tee -a "$LOG_FILE"

echo "删除操作完成。删除的文件和文件夹已记录在 $LOG_FILE 中。"