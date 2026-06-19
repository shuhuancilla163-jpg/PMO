# PMO Dockerfile
# 0.0.7 解耦: 治理规则不绑工程, Docker 是工程实现层候选之一
# Q2: PMO 本地优先, Docker 用于容器可扩展 (后期多项目)
# DEC-2026-0002: 8 PMO 角色 (5 → 8, 按 3 维度严格分离)

FROM python:3.11-slim

# 元信息
LABEL maintainer="Sponsor <sponsor@local>"
LABEL version="0.3.0"
LABEL description="PMO Platform - 1 套 PMO 治理规范, 1 个 PMO 实例, 8 PMO 角色 (按 3 维度严格分离), N 个业务项目复用"
LABEL architecture="1-spec-8-roles-N-projects"
LABEL decision="DEC-2026-0002"

# 工作目录
WORKDIR /pmo

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制 PMO 代码
COPY . /pmo/

# 暴露端口 (MCP / API, 后期)
# EXPOSE 8080

# 健康检查 (DEC-2026-0002: 8 PMO 角色)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.path.insert(0, '/pmo/scripts/runtime'); from agents.agent_base import PMOInstance; pmo = PMOInstance('/pmo'); assert len(pmo.agents) == 8, f'Expected 8 PMO roles, got {len(pmo.agents)}'; print('OK')" || exit 1

# 启动命令
CMD ["bash", "/pmo/scripts/start.sh"]
