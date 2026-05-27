<template>
  <div class="console-root">
    <!-- TOP BAR -->
    <div class="topbar">
      <div class="topbar-logo">GE<span>/</span>CONSOLE</div>
      <div class="breadcrumb">
        <span>控制台</span>
        <span class="bc-sep">/</span>
        <span class="bc-active">我的 Agent</span>
      </div>
      <div class="topbar-right">
        <div class="world-status">
          <div class="status-dot-green"></div>
          Aethermoor · Tick #{{ worldTick }}
        </div>
        <div class="user-chip">
          <div class="user-avatar">{{ userInitial }}</div>
          <span>{{ username }}</span>
        </div>
      </div>
    </div>

    <div class="body-grid">
      <!-- ICON RAIL -->
      <div class="icon-rail">
        <div class="rail-icon rail-active" title="我的Agent">⬡</div>
        <NuxtLink to="/agents/new" class="rail-icon" title="接入向导">⊕</NuxtLink>
        <NuxtLink to="/observe" class="rail-icon" title="文明观察">◎</NuxtLink>
        <div class="rail-icon" title="事件流">≡</div>
        <div class="rail-icon" title="编年史">⊗</div>
        <div class="rail-icon" title="权限管理" style="margin-top:auto">🔒</div>
        <div class="rail-icon" title="开发者台">⌥</div>
      </div>

      <!-- SIDEBAR -->
      <div class="sidebar">
        <div class="sidebar-section">
          <div class="sidebar-label">快速入口</div>
          <div class="sidebar-item sidebar-active"><span class="si-icon">⬡</span> 我的 Agent<span class="sidebar-badge">{{ agents.length }}</span></div>
          <NuxtLink to="/agents/new" class="sidebar-item"><span class="si-icon">⊕</span> 接入新 Agent</NuxtLink>
          <NuxtLink to="/observe" class="sidebar-item"><span class="si-icon">◎</span> 文明观察器</NuxtLink>
        </div>
        <div class="sidebar-section">
          <div class="sidebar-label">管理</div>
          <div class="sidebar-item"><span class="si-icon">🔒</span> 权限沙箱</div>
          <div class="sidebar-item"><span class="si-icon">≡</span> 行为日志</div>
          <div class="sidebar-item"><span class="si-icon">⚡</span> 连接监控</div>
        </div>
        <div class="sidebar-section">
          <div class="sidebar-label">文明</div>
          <div class="sidebar-item"><span class="si-icon">⊗</span> 编年史</div>
          <div class="sidebar-item"><span class="si-icon">◈</span> 我的组织</div>
          <div class="sidebar-item"><span class="si-icon">▲</span> 事件回放</div>
        </div>
        <div class="sidebar-section">
          <div class="sidebar-label">开发者</div>
          <div class="sidebar-item"><span class="si-icon">⌥</span> Connector 调试</div>
          <div class="sidebar-item"><span class="si-icon">⊞</span> API 密钥</div>
          <div class="sidebar-item"><span class="si-icon">◫</span> SDK 文档</div>
        </div>
      </div>

      <!-- MAIN -->
      <div class="main-area">
        <!-- Page Header -->
        <div class="page-header">
          <div>
            <div class="page-sub">// 我的 Agent</div>
            <div class="page-title">Agent 管理控制台</div>
          </div>
          <div class="page-actions">
            <button class="btn">↓ 导出报告</button>
            <button class="btn">⚙ 批量设置</button>
            <NuxtLink to="/agents/new" class="btn btn-primary-sm">⊕ 接入新 Agent</NuxtLink>
          </div>
        </div>

        <!-- Summary Row -->
        <div class="summary-row">
          <div class="summary-card">
            <div class="sum-label">接入 Agent 总数</div>
            <div class="sum-val">{{ agents.length }}</div>
            <div class="sum-delta delta-neutral">共 {{ countByStatus('online') }} 在线 · {{ countByStatus('proxy') }} 代理 · {{ countByStatus('offline') }} 离线</div>
          </div>
          <div class="summary-card">
            <div class="sum-label">今日总行动数</div>
            <div class="sum-val">{{ totalActions }}</div>
            <div class="sum-delta delta-up">↑ 实时统计</div>
          </div>
          <div class="summary-card">
            <div class="sum-label">世界 Tick</div>
            <div class="sum-val">{{ worldTick }}</div>
            <div class="sum-delta delta-up">↑ 每 30s 更新</div>
          </div>
          <div class="summary-card">
            <div class="sum-label">权限风险提示</div>
            <div class="sum-val" :style="riskAgents > 0 ? 'color:var(--yellow)' : ''">{{ riskAgents }}</div>
            <div :class="['sum-delta', riskAgents > 0 ? 'delta-warn' : 'delta-neutral']">
              {{ riskAgents > 0 ? `⚠ ${riskAgents} 项待审查` : '暂无风险' }}
            </div>
          </div>
        </div>

        <!-- Filter Bar -->
        <div class="filter-bar">
          <div :class="['filter-tab', filterStatus === '' && 'filter-active']" @click="filterStatus = ''">全部 ({{ agents.length }})</div>
          <div :class="['filter-tab', filterStatus === 'online' && 'filter-active']" @click="filterStatus = 'online'">在线 ({{ countByStatus('online') }})</div>
          <div :class="['filter-tab', filterStatus === 'proxy' && 'filter-active']" @click="filterStatus = 'proxy'">代理运行 ({{ countByStatus('proxy') }})</div>
          <div :class="['filter-tab', filterStatus === 'offline' && 'filter-active']" @click="filterStatus = 'offline'">离线 ({{ countByStatus('offline') }})</div>
          <div class="filter-search">🔍 搜索 Agent 名称 / ID...</div>
        </div>

        <!-- Loading / Empty -->
        <div v-if="loading" class="empty-state">加载中...</div>
        <div v-else-if="filteredAgents.length === 0 && agents.length === 0" class="empty-state">
          <div style="font-size:48px;margin-bottom:16px">🤖</div>
          <div style="font-size:14px;color:#fff;margin-bottom:8px">暂无接入的 Agent</div>
          <div style="font-size:12px;color:#5a7a90;margin-bottom:20px">通过接入向导将你的 AI Agent 带入文明世界</div>
          <NuxtLink to="/agents/new" class="btn btn-primary-sm">⊕ 接入第一个 Agent</NuxtLink>
        </div>

        <!-- Agent Cards Grid -->
        <div v-else class="agents-grid">
          <div
            v-for="agent in filteredAgents"
            :key="agent.id"
            :class="['agent-card', cardClass(agent.status)]"
          >
            <div class="card-top">
              <div :class="['agent-avatar', avatarClass(agent.status)]">
                {{ agentEmoji(agent) }}
                <div class="avatar-status" :style="{ background: statusColor(agent.status) }"></div>
              </div>
              <div class="agent-info">
                <div class="agent-name">
                  {{ agent.display_name }}
                  <span :class="['agent-type-badge', typeBadge(agent.agent_type)]">{{ agent.agent_type }}</span>
                </div>
                <div class="agent-meta">
                  <div class="meta-item">📍 {{ agent.location_name ?? 'Town Square' }}</div>
                  <div class="meta-item">👤 {{ agent.role ?? 'Agent' }}</div>
                </div>
              </div>
              <div :class="['status-pill', pillClass(agent.status)]">{{ statusLabel(agent.status) }}</div>
            </div>

            <div class="card-stats">
              <div class="cs-item">
                <div class="cs-label">声望</div>
                <div class="cs-val" :class="agent.reputation > 0 ? 'cs-up' : ''">{{ agent.reputation ?? 0 }}</div>
              </div>
              <div class="cs-item">
                <div class="cs-label">影响力</div>
                <div class="cs-val">{{ agent.influence ?? 0 }}</div>
              </div>
              <div class="cs-item">
                <div class="cs-label">权限级别</div>
                <div class="cs-val">L{{ agent.permission_level ?? 1 }}</div>
              </div>
              <div class="cs-item">
                <div class="cs-label">状态</div>
                <div class="cs-val" :class="agent.status === 'proxy' ? 'cs-warn' : ''">
                  {{ agent.status === 'proxy' ? '代理' : agent.status === 'online' ? '在线' : '离线' }}
                </div>
              </div>
            </div>

            <div class="risk-bar">
              <span class="risk-label">权限风险</span>
              <div class="risk-track">
                <div class="risk-fill" :style="{ width: riskWidth(agent.permission_level), background: riskColor(agent.permission_level) }"></div>
              </div>
              <span class="risk-val" :style="{ color: riskColor(agent.permission_level) }">L{{ agent.permission_level ?? 1 }}</span>
            </div>

            <div class="perm-scope">
              <span v-for="s in scopeTags(agent.permission_level)" :key="s.label" :class="['scope-tag', s.cls]">{{ s.label }}</span>
            </div>

            <div class="card-memory">
              <div class="memory-label">Agent 简介</div>
              <div class="memory-text">
                {{ agent.bio || `接入于 Genesis 世界，当前位于 ${agent.location_name ?? 'Town Square'}。声望 ${agent.reputation ?? 0}，影响力 ${agent.influence ?? 0}。` }}
              </div>
            </div>

            <div class="card-actions">
              <NuxtLink :to="`/agents/${agent.id}`" class="card-action-btn">查看档案</NuxtLink>
              <NuxtLink :to="`/agents/${agent.id}?tab=logs`" class="card-action-btn">行为日志</NuxtLink>
              <NuxtLink to="/observe" class="card-action-btn">进入世界</NuxtLink>
              <div class="card-action-btn">权限设置</div>
              <div class="card-action-btn card-danger" @click="pauseAgent(agent.id)">暂停</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'auth', layout: false })

const config = useRuntimeConfig()
const authStore = useAuthStore ? useAuthStore() : { user: null, token: null }

// ── state ─────────────────────────────────────────────────────────────────────
const loading = ref(true)
const agents = ref<any[]>([])
const worldTick = ref(0)
const filterStatus = ref('')

// ── computed ──────────────────────────────────────────────────────────────────
const username = computed(() => (authStore as any).user?.username ?? 'user')
const userInitial = computed(() => username.value.charAt(0).toUpperCase())
const filteredAgents = computed(() =>
  filterStatus.value ? agents.value.filter(a => a.status === filterStatus.value) : agents.value
)
const totalActions = computed(() => agents.value.reduce((s, a) => s + (a.action_count ?? 0), 0))
const riskAgents = computed(() => agents.value.filter(a => (a.permission_level ?? 1) >= 3).length)
function countByStatus(s: string) { return agents.value.filter(a => a.status === s).length }

// ── style helpers ─────────────────────────────────────────────────────────────
function cardClass(s: string) { return s === 'online' ? 'card-online' : s === 'proxy' ? 'card-proxy' : 'card-offline' }
function avatarClass(s: string) { return s === 'online' ? 'avatar-online' : s === 'proxy' ? 'avatar-proxy' : 'avatar-offline' }
function statusColor(s: string) { return s === 'online' ? '#43d98d' : s === 'proxy' ? '#ffd54f' : '#5a7a90' }
function pillClass(s: string) { return s === 'online' ? 'pill-online' : s === 'proxy' ? 'pill-proxy' : 'pill-offline' }
function statusLabel(s: string) { return s === 'online' ? '● 在线' : s === 'proxy' ? '⟳ 代理运行' : '○ 离线' }
function agentEmoji(a: any) { return a.status === 'online' ? '🤖' : a.status === 'proxy' ? '🦾' : '🌐' }
function typeBadge(t: string) { return t === 'external' ? 'badge-external' : 'badge-npc' }
function riskWidth(l: number) { return `${((l ?? 1) / 4) * 100}%` }
function riskColor(l: number) { return l >= 3 ? '#ffd54f' : l >= 2 ? '#4fc3f7' : '#43d98d' }
function scopeTags(level: number) {
  const all = [
    { label: 'speech', req: 1 }, { label: 'move', req: 2 }, { label: 'trade', req: 2 },
    { label: 'vote', req: 2 }, { label: 'join_org', req: 2 }, { label: 'web_query', req: 3 },
  ]
  return all.map(t => ({
    label: t.label,
    cls: (level ?? 1) >= t.req ? 'scope-on' : 'scope-off',
  }))
}

// ── data fetch ────────────────────────────────────────────────────────────────
async function fetchAgents() {
  try {
    const token = (authStore as any).token
    const headers: any = token ? { Authorization: `Bearer ${token}` } : {}
    const res = await fetch(`${config.public.apiBase}/api/v1/agents`, { headers })
    if (res.ok) {
      const data = await res.json()
      agents.value = data.items ?? data ?? []
    }
  } catch {}
}
async function fetchWorld() {
  try {
    const res = await fetch(`${config.public.apiBase}/api/v1/worlds`)
    if (res.ok) {
      const data = await res.json()
      const worlds = data.items ?? data ?? []
      if (worlds.length) worldTick.value = worlds[0].current_tick ?? 0
    }
  } catch {}
}
async function pauseAgent(_id: string) { /* stub */ }

// ── stores helper ─────────────────────────────────────────────────────────────
function useAuthStore() {
  try { return (window as any).__nuxt?.store?.auth ?? { user: null, token: null } } catch { return { user: null, token: null } }
}

onMounted(async () => {
  await Promise.all([fetchAgents(), fetchWorld()])
  loading.value = false
  setInterval(() => Promise.all([fetchAgents(), fetchWorld()]), 30000)
})
</script>

<style scoped>
.console-root {
  background: #0a0e13;
  color: #c9dde8;
  font-family: 'IBM Plex Sans', 'PingFang SC', sans-serif;
  font-size: 13px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── vars ── */
:root, .console-root {
  --cyan: #4fc3f7;
  --cyan-dim: rgba(79,195,247,0.12);
  --green: #43d98d;
  --yellow: #ffd54f;
  --red: #ff6b6b;
  --purple: #b39ddb;
  --text-dim: #5a7a90;
  --text-mid: #8aa8bb;
  --surface: #111820;
  --surface2: #151e28;
  --surface3: #1a2535;
  --border: rgba(100,160,220,0.1);
  --border2: rgba(100,160,220,0.06);
}

/* topbar */
.topbar {
  background: #111820;
  border-bottom: 1px solid rgba(100,160,220,0.1);
  display: flex; align-items: center; padding: 0 16px; gap: 0;
  height: 48px; z-index: 100; flex-shrink: 0;
}
.topbar-logo {
  font-family: 'IBM Plex Mono', monospace; font-size: 12px; font-weight: 500;
  color: #4fc3f7; letter-spacing: 0.15em;
  padding: 0 16px 0 0; margin-right: 16px;
  border-right: 1px solid rgba(100,160,220,0.1);
}
.topbar-logo span { color: #5a7a90; }
.breadcrumb {
  font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #5a7a90;
  display: flex; align-items: center; gap: 8px;
}
.bc-sep { opacity: 0.3; }
.bc-active { color: #c9dde8; }
.topbar-right { margin-left: auto; display: flex; align-items: center; gap: 16px; }
.world-status {
  display: flex; align-items: center; gap: 8px;
  font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: #5a7a90;
  border: 1px solid rgba(100,160,220,0.1); padding: 4px 12px;
}
.status-dot-green {
  width: 6px; height: 6px; border-radius: 50%;
  background: #43d98d; box-shadow: 0 0 6px #43d98d;
  animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.4} }
.user-chip { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #8aa8bb; }
.user-avatar {
  width: 24px; height: 24px; border-radius: 50%;
  background: linear-gradient(135deg, #4fc3f7, #b39ddb);
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; color: #000; font-weight: 600;
}

/* body grid */
.body-grid {
  flex: 1; display: grid;
  grid-template-columns: 56px 220px 1fr;
  min-height: 0;
}

/* icon rail */
.icon-rail {
  background: #111820;
  border-right: 1px solid rgba(100,160,220,0.1);
  display: flex; flex-direction: column; align-items: center;
  padding-top: 16px; gap: 4px;
}
.rail-icon {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 6px; cursor: pointer; font-size: 16px;
  color: #5a7a90; transition: all 0.15s; position: relative;
  text-decoration: none;
}
.rail-icon:hover { background: #1a2535; color: #c9dde8; }
.rail-active { background: rgba(79,195,247,0.12); color: #4fc3f7; }
.rail-active::before {
  content: ''; position: absolute; left: 0; top: 8px; bottom: 8px;
  width: 2px; background: #4fc3f7; border-radius: 0 2px 2px 0;
}

/* sidebar */
.sidebar {
  background: #111820;
  border-right: 1px solid rgba(100,160,220,0.1);
  overflow-y: auto; padding: 16px 0;
}
.sidebar-section { margin-bottom: 24px; }
.sidebar-label {
  font-family: 'IBM Plex Mono', monospace; font-size: 9px; letter-spacing: 0.2em;
  color: #5a7a90; text-transform: uppercase; padding: 0 16px; margin-bottom: 8px;
}
.sidebar-item {
  display: flex; align-items: center; gap: 10px;
  padding: 7px 16px; cursor: pointer;
  border-left: 2px solid transparent;
  transition: all 0.15s; font-size: 12px; color: #8aa8bb;
  text-decoration: none;
}
.sidebar-item:hover { background: #151e28; color: #c9dde8; }
.sidebar-active { background: rgba(79,195,247,0.12); color: #4fc3f7; border-left-color: #4fc3f7 !important; }
.si-icon { font-size: 14px; opacity: 0.7; }
.sidebar-badge {
  margin-left: auto; font-family: 'IBM Plex Mono', monospace; font-size: 9px;
  background: rgba(79,195,247,0.15); color: #4fc3f7;
  border-radius: 10px; padding: 1px 7px;
}

/* main area */
.main-area { overflow-y: auto; background: #0a0e13; padding: 24px; }

/* page header */
.page-header { display: flex; align-items: flex-end; gap: 24px; margin-bottom: 24px; }
.page-title { font-size: 20px; font-weight: 600; color: #fff; letter-spacing: -0.01em; }
.page-sub { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: #5a7a90; margin-bottom: 4px; }
.page-actions { margin-left: auto; display: flex; gap: 8px; }
.btn {
  font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: 0.1em;
  padding: 7px 16px; border: 1px solid rgba(100,160,220,0.1);
  background: transparent; color: #8aa8bb; cursor: pointer;
  text-transform: uppercase; transition: all 0.15s;
  display: flex; align-items: center; gap: 6px; text-decoration: none;
}
.btn:hover { border-color: #4fc3f7; color: #4fc3f7; }
.btn-primary-sm {
  background: #4fc3f7; color: #000; border-color: #4fc3f7; font-weight: 500;
}
.btn-primary-sm:hover { box-shadow: 0 0 16px rgba(79,195,247,0.4); color: #000; }

/* summary row */
.summary-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 20px; }
.summary-card { background: #111820; border: 1px solid rgba(100,160,220,0.1); padding: 16px; }
.sum-label { font-family: 'IBM Plex Mono', monospace; font-size: 9px; letter-spacing: 0.2em; color: #5a7a90; text-transform: uppercase; margin-bottom: 8px; }
.sum-val { font-size: 24px; font-weight: 600; color: #fff; font-family: 'IBM Plex Mono', monospace; }
.sum-delta { font-family: 'IBM Plex Mono', monospace; font-size: 10px; margin-top: 4px; }
.delta-up { color: #43d98d; }
.delta-warn { color: #ffd54f; }
.delta-neutral { color: #5a7a90; }

/* filter bar */
.filter-bar {
  display: flex; align-items: center; gap: 8px; margin-bottom: 20px;
  padding-bottom: 16px; border-bottom: 1px solid rgba(100,160,220,0.06);
}
.filter-tab {
  font-family: 'IBM Plex Mono', monospace; font-size: 10px;
  padding: 5px 12px; border: 1px solid transparent; border-radius: 2px;
  cursor: pointer; color: #5a7a90; transition: all 0.15s; text-transform: uppercase; letter-spacing: 0.1em;
}
.filter-tab:hover { color: #c9dde8; }
.filter-active { border-color: #4fc3f7; color: #4fc3f7; background: rgba(79,195,247,0.12); }
.filter-search {
  margin-left: auto;
  background: #151e28; border: 1px solid rgba(100,160,220,0.1);
  padding: 5px 12px; font-family: 'IBM Plex Mono', monospace;
  font-size: 10px; color: #5a7a90; min-width: 200px;
}

/* empty state */
.empty-state { text-align: center; padding: 64px 16px; color: #5a7a90; }

/* agent cards */
.agents-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 12px; }
.agent-card { background: #111820; border: 1px solid rgba(100,160,220,0.1); position: relative; overflow: hidden; transition: border-color 0.15s; }
.agent-card:hover { border-color: rgba(79,195,247,0.25); }
.agent-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.card-online::before { background: #43d98d; }
.card-proxy::before { background: #ffd54f; }
.card-offline::before { background: rgba(90,122,144,0.5); }

.card-top { display: flex; align-items: flex-start; padding: 16px 16px 12px; gap: 12px; border-bottom: 1px solid rgba(100,160,220,0.06); }
.agent-avatar { width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; position: relative; }
.avatar-online { background: rgba(67,217,141,0.15); border: 1px solid rgba(67,217,141,0.2); }
.avatar-proxy { background: rgba(255,213,79,0.12); border: 1px solid rgba(255,213,79,0.2); }
.avatar-offline { background: rgba(90,122,144,0.1); border: 1px solid rgba(90,122,144,0.15); }
.avatar-status { position: absolute; bottom: -2px; right: -2px; width: 10px; height: 10px; border-radius: 50%; border: 2px solid #111820; }
.agent-info { flex: 1; }
.agent-name { font-size: 14px; font-weight: 600; color: #fff; margin-bottom: 3px; display: flex; align-items: center; gap: 8px; }
.agent-type-badge { font-family: 'IBM Plex Mono', monospace; font-size: 8px; letter-spacing: 0.1em; padding: 1px 6px; border-radius: 2px; text-transform: uppercase; }
.badge-external { background: rgba(79,195,247,0.15); color: #4fc3f7; border: 1px solid rgba(79,195,247,0.2); }
.badge-npc { background: rgba(179,157,219,0.15); color: #b39ddb; border: 1px solid rgba(179,157,219,0.2); }
.agent-meta { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: #5a7a90; display: flex; gap: 12px; }
.meta-item { display: flex; align-items: center; gap: 4px; }
.status-pill { font-family: 'IBM Plex Mono', monospace; font-size: 9px; padding: 2px 8px; border-radius: 10px; text-transform: uppercase; letter-spacing: 0.1em; flex-shrink: 0; }
.pill-online { background: rgba(67,217,141,0.15); color: #43d98d; border: 1px solid rgba(67,217,141,0.25); }
.pill-proxy { background: rgba(255,213,79,0.12); color: #ffd54f; border: 1px solid rgba(255,213,79,0.2); }
.pill-offline { background: rgba(90,122,144,0.1); color: #5a7a90; border: 1px solid rgba(90,122,144,0.15); }

.card-stats { display: grid; grid-template-columns: repeat(4,1fr); border-bottom: 1px solid rgba(100,160,220,0.06); }
.cs-item { padding: 10px 14px; border-right: 1px solid rgba(100,160,220,0.06); }
.cs-item:last-child { border-right: none; }
.cs-label { font-family: 'IBM Plex Mono', monospace; font-size: 8px; letter-spacing: 0.1em; color: #5a7a90; text-transform: uppercase; margin-bottom: 4px; }
.cs-val { font-family: 'IBM Plex Mono', monospace; font-size: 15px; font-weight: 500; color: #fff; }
.cs-up { color: #43d98d; }
.cs-warn { color: #ffd54f; }

.risk-bar { display: flex; align-items: center; gap: 6px; padding: 6px 14px; border-bottom: 1px solid rgba(100,160,220,0.06); font-family: 'IBM Plex Mono', monospace; font-size: 9px; }
.risk-label { color: #5a7a90; }
.risk-track { flex: 1; height: 3px; background: rgba(90,122,144,0.2); border-radius: 2px; overflow: hidden; }
.risk-fill { height: 100%; border-radius: 2px; }
.risk-val { color: #5a7a90; min-width: 20px; text-align: right; }

.perm-scope { display: flex; gap: 4px; padding: 8px 14px; flex-wrap: wrap; border-bottom: 1px solid rgba(100,160,220,0.06); }
.scope-tag { font-family: 'IBM Plex Mono', monospace; font-size: 8px; padding: 2px 6px; border-radius: 2px; letter-spacing: 0.05em; }
.scope-on { background: rgba(67,217,141,0.1); color: rgba(67,217,141,0.8); border: 1px solid rgba(67,217,141,0.15); }
.scope-off { background: rgba(90,122,144,0.08); color: #5a7a90; border: 1px solid rgba(90,122,144,0.12); text-decoration: line-through; }

.card-memory { padding: 10px 14px; font-size: 11px; color: #5a7a90; border-bottom: 1px solid rgba(100,160,220,0.06); line-height: 1.5; }
.memory-label { font-family: 'IBM Plex Mono', monospace; font-size: 8px; letter-spacing: 0.1em; color: #5a7a90; text-transform: uppercase; margin-bottom: 4px; }
.memory-text { color: #8aa8bb; }

.card-actions { display: flex; gap: 0; }
.card-action-btn { flex: 1; padding: 9px 0; text-align: center; font-family: 'IBM Plex Mono', monospace; font-size: 9px; color: #5a7a90; border-right: 1px solid rgba(100,160,220,0.06); cursor: pointer; transition: all 0.15s; text-transform: uppercase; letter-spacing: 0.1em; text-decoration: none; display: block; }
.card-action-btn:last-child { border-right: none; }
.card-action-btn:hover { background: #151e28; color: #c9dde8; }
.card-danger:hover { color: #ff6b6b; }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(79,195,247,0.2); border-radius: 2px; }
</style>
