#!/usr/bin/env bash
# Memento Lite — systemd 守护进程一键配置
# 用法: sudo bash setup-daemon.sh
set -euo pipefail

APP_DIR="/opt/Memento"
SERVICE_FILE="/etc/systemd/system/memento.service"

# 必须 root
if [ "$(id -u)" -ne 0 ]; then
    echo "请用 sudo 运行: sudo bash setup-daemon.sh"
    exit 1
fi

echo "=== 配置 systemd 守护进程 ==="

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Memento Lite (Agnes AI 全模态测试台)
After=network.target

[Service]
Type=simple
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
EnvironmentFile=${APP_DIR}/.env

[Install]
WantedBy=multi-user.target
EOF

echo "✓ 服务文件已创建: $SERVICE_FILE"

# 停掉可能在前台跑的 uvicorn
echo "=== 停止当前前台进程 ==="
pkill -f "uvicorn backend.main:app" 2>/dev/null || true
sleep 1

# 重载并启动
systemctl daemon-reload
systemctl enable memento
systemctl restart memento

sleep 2

echo "=== 检查状态 ==="
systemctl status memento --no-pager -l | head -15

echo ""
echo "=== 完成 ==="
echo "服务已启动并设为开机自启"
echo ""
echo "常用命令:"
echo "  查看状态:  systemctl status memento"
echo "  查看日志:  journalctl -u memento -f"
echo "  重启服务:  systemctl restart memento"
echo "  停止服务:  systemctl stop memento"
echo ""
echo "现在可以关掉 SSH，服务会持续运行。"
