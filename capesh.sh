#!/bin/bash

echo "請選擇操作："
echo "1) 停止 CAPE 和相關服務"
echo "2) 重新啟動 CAPE 和相關服務"
echo "3) 手動執行 cuckoo.py"
echo "4) 手動清理 CAPE 數據"
read -p "輸入你的選擇 (1, 2, 3, 4): " choice

case $choice in
  1)
    echo "停止 CAPE 和相關服務..."
    sudo systemctl stop cape.service
    sudo systemctl stop cape-processor.service
    sudo systemctl stop cape-web.service
    sudo systemctl stop cape-rooter.service
    ;;
  2)
    echo "重新啟動 CAPE 和相關服務..."
    sudo systemctl restart cape.service
    sudo systemctl restart cape-processor.service
    sudo systemctl restart cape-web.service
    sudo systemctl restart cape-rooter.service
    ;;
  3)
    echo "手動執行 cuckoo.py..."
    cd /opt/CAPEv2  # 替換為 cuckoo.py 的實際路徑
    poetry run python cuckoo.py
    ;;
  4)
    echo "手動清理 CAPE 數據..."
    cd /opt/CAPEv2  # 替換為 cleaners.py 的實際路徑
    poetry run python /opt/CAPEv2/utils/cleaners.py --clean
    ;;
  *)
    echo "無效的選擇，請重新運行腳本。"
    ;;
esac
