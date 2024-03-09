#!/usr/bin/env bash
# 遇到錯誤時終止腳本
set -o errexit

STORAGE_DIR=/opt/render/project/.render

if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "正在下載 Chrome..."
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
  cd $HOME/project/src # 確保我們返回到原本的位置
  echo "Chrome 安裝完成。"
else
  echo "從快取中使用 Chrome。"
fi

# 確保將 Chrome 的位置添加到啟動命令的 PATH 中
export PATH="${PATH}:/opt/render/project/.render/chrome/opt/google/chrome/";

# 在此添加您自己的構建命令...
