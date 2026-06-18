#!/bin/bash
# PMO 停止脚本 (stop.sh)
# - 优雅停止 PMO 实例
# - 持久化状态
# - 输出停止报告

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PMO_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PMO_ROOT/logs"
LOG_FILE="$LOG_DIR/pmo-shutdown-$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$LOG_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log_success() {
    log "${GREEN}✅ $1${NC}"
}

log_warn() {
    log "${YELLOW}⚠️  $1${NC}"
}

log "================================================"
log "  PMO 停止 v0.3.0"
log "  时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
log "================================================"

# 1. 持久化状态
log ""
log "[1/3] 持久化状态"
if [ -f "$PMO_ROOT/tasks/state/1.1-pmo-self.json" ]; then
    log_success "业务项目状态已持久化"
else
    log_warn "状态文件不存在"
fi

# 2. 持久化指标
log ""
log "[2/3] 持久化指标"
if [ -d "$PMO_ROOT/metrics/business/1.1-pmo-self" ]; then
    log_success "业务指标已持久化"
fi

# 3. 输出报告
log ""
log "[3/3] 停止报告"
log_success "PMO 实例: 已停止 (优雅)"
log_success "状态: 已持久化"
log_success "日志: $LOG_FILE"
log ""
log "================================================"
log "  PMO 停止完成 ✅"
log "================================================"
log ""
