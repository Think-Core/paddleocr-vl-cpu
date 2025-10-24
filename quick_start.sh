#!/bin/bash

SESSION_NAME="paddleocr-api"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR"

case "$1" in
    start)
        echo "启动 PaddleOCR API..."
        echo "工作目录: $WORK_DIR"
        
        # 检查必要文件
        if [ ! -f "$WORK_DIR/paddleocr_api.py" ]; then
            echo "错误: 找不到 paddleocr_api.py"
            exit 1
        fi
        
        if [ ! -d "$WORK_DIR/paddleocrvl" ]; then
            echo "错误: 找不到虚拟环境 paddleocrvl/"
            exit 1
        fi
        
        tmux has-session -t $SESSION_NAME 2>/dev/null
        if [ $? == 0 ]; then
            echo "服务已在运行！"
            exit 1
        fi
        
        tmux new-session -d -s $SESSION_NAME -c "$WORK_DIR"
        tmux send-keys -t $SESSION_NAME "cd $WORK_DIR" C-m
        tmux send-keys -t $SESSION_NAME "source paddleocrvl/bin/activate" C-m
        tmux send-keys -t $SESSION_NAME "python paddleocr_api.py" C-m
        
        echo "✓ 服务已启动"
        ;;
        
    stop)
        echo "停止服务..."
        tmux kill-session -t $SESSION_NAME 2>/dev/null
        echo "✓ 服务已停止"
        ;;
        
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
        
    attach)
        tmux attach -t $SESSION_NAME
        ;;
        
    status)
        tmux has-session -t $SESSION_NAME 2>/dev/null
        if [ $? == 0 ]; then
            echo "✓ 服务运行中"
        else
            echo "✗ 服务未运行"
        fi
        ;;
        
    *)
        echo "用法: $0 {start|stop|restart|attach|status}"
        exit 1
        ;;
esac



# 启动服务
#./tmux_manage.sh start

# 停止服务
#./tmux_manage.sh stop

# 重启服务
#./tmux_manage.sh restart

# 查看服务
#./tmux_manage.sh attach

# 检查状态
#./tmux_manage.sh status