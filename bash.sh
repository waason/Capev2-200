#!/bin/bash

# 提示输入一次 sudo 密码并存储
echo "請輸入您的 sudo 密碼："
read -s PASSWORD

# 定义服务列表
services=(
    "cape.service"
    "cape-processor.service"
    "cape-web.service"
    "cape-rooter.service"
)

# 在每个新终端窗口中监控各个服务的日志
for service in "${services[@]}"; do
    gnome-terminal -- bash -c "echo $PASSWORD | sudo -S journalctl -u $service -f; exec bash"
done
