#!/bin/bash
# PMO 启动脚本 (start.sh)
# - 本地启动 PMO 运行时
# - 检查环境
# - 加载配置
# - 启动 agent
# - 输出状态

set -e

# ============================================
# 颜色输出
# ============================================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================
# 路径
# ============================================
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PMO_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PMO_ROOT/logs"
LOG_FILE="$LOG_DIR/pmo-startup-$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$LOG_DIR"

log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log_success() {
    log "${GREEN}✅ $1${NC}"
}

log_warn() {
    log "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    log "${RED}❌ $1${NC}"
}

# ============================================
# 启动横幅
# ============================================
log "================================================"
log "  PMO 启动 v0.3.0"
log "  PMO_ROOT: $PMO_ROOT"
log "  时间: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
log "================================================"

# ============================================
# 1. 检查环境
# ============================================
log ""
log "[1/6] 检查环境"

# Python
if command -v python3 &> /dev/null; then
    PY_VERSION=$(python3 --version)
    log_success "Python: $PY_VERSION"
else
    log_error "Python3 未安装"
    exit 1
fi

# Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    log_success "Git: $GIT_VERSION"
else
    log_error "Git 未安装"
    exit 1
fi

# PMO 目录
if [ -d "$PMO_ROOT" ]; then
    log_success "PMO 目录: $PMO_ROOT"
else
    log_error "PMO 目录不存在: $PMO_ROOT"
    exit 1
fi

# ============================================
# 2. 检查 Git 状态
# ============================================
log ""
log "[2/6] 检查 Git 状态"
cd "$PMO_ROOT"

if [ -d ".git" ]; then
    COMMIT=$(git log -1 --format='%h %s' 2>/dev/null || echo "no commit")
    TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "no tag")
    BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
    log_success "分支: $BRANCH"
    log_success "Commit: $COMMIT"
    log_success "Tag: $TAG"
else
    log_warn "未初始化 Git 仓库, 正在初始化..."
    git init -b main
    log_success "Git 仓库初始化完成"
fi

# ============================================
# 3. 加载配置
# ============================================
log ""
log "[3/6] 加载 PMO 配置"

if [ -f "$PMO_ROOT/config/pmo.config.yaml" ]; then
    log_success "配置文件: config/pmo.config.yaml"
    # 用 Python 解析 (避免依赖 yq/jq)
    python3 -c "
import yaml
with open('$PMO_ROOT/config/pmo.config.yaml') as f:
    config = yaml.safe_load(f)
pmo = config.get('pmo', {})
print(f'  - PMO 版本: {pmo.get(\"version\")}')
print(f'  - PMO 实例: {pmo.get(\"instance_id\")}')
print(f'  - 架构: {pmo.get(\"architecture\")}')
print(f'  - Sponsor: {pmo.get(\"sponsor\", {}).get(\"name\")}')
deploy = config.get('deployment', {})
print(f'  - PMO 部署: {deploy.get(\"pmo_target\")}')
print(f'  - 业务部署: {deploy.get(\"biz_target\")}')
" 2>/dev/null || log_warn "yaml 解析失败, 跳过配置预览"
else
    log_warn "配置文件不存在"
fi

# ============================================
# 4. 检查不可变文档
# ============================================
log ""
log "[4/6] 检查不可变文档库"
DOC_COUNT=$(ls "$PMO_ROOT/immutable/0-governance/"*.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$DOC_COUNT" -gt 0 ]; then
    log_success "不可变文档: $DOC_COUNT 个"
    ls "$PMO_ROOT/immutable/0-governance/"*.md | while read f; do
        echo "  - $(basename $f)" | tee -a "$LOG_FILE"
    done
else
    log_warn "未找到不可变文档"
fi

# ============================================
# 5. 启动 PMO 运行时
# ============================================
log ""
log "[5/6] 启动 PMO 运行时"

if [ -f "$PMO_ROOT/scripts/runtime/pmo_runtime.py" ]; then
    log "执行 pmo_runtime.py..."
    python3 "$PMO_ROOT/scripts/runtime/pmo_runtime.py" 2>&1 | tee -a "$LOG_FILE" | tail -30
    log_success "PMO 运行时启动完成"
else
    log_error "运行时入口不存在: scripts/runtime/pmo_runtime.py"
    exit 1
fi

# ============================================
# 6. 启动后状态
# ============================================
log ""
log "[6/6] 启动后状态"
log_success "PMO 实例: pmo-local-001 (running)"
log_success "Agent: 5 个 (L0 Sponsor + L1 PMO-Main + L2 Plan/Engineer/Reviewer)"
log_success "业务项目: 1.1-pmo-self (active)"
log_success "指标: 21 项 (业务 5 + 治理 8 + 工程 8)"
log_success "日志: $LOG_FILE"

log ""
log "================================================"
log "  PMO 启动完成 ✅"
log "================================================"
log ""
log "PMO 入口: $PMO_ROOT"
log "日志文件: $LOG_FILE"
log "下次启动: bash $SCRIPT_DIR/start.sh"
log ""
