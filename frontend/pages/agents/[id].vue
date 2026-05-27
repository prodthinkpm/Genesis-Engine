<template>
  <div class="console-root">

    <!-- TOP BAR -->
    <div class="topbar">
      <div class="topbar-logo">GE<span>/</span>CONSOLE</div>
      <div class="breadcrumb">
        <span>控制台</span>
        <span class="bc-sep">/</span>
        <NuxtLink to="/dashboard" class="bc-link">我的 Agent</NuxtLink>
        <span class="bc-sep">/</span>
        <span class="bc-active">{{ agent?.display_name || '加载中...' }}</span>
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
          <div class="sidebar-item sidebar-active"><span class="si-icon">⬡</span> 我的 Agent</div>
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

        <!-- Loading state -->
        <div v-if="!agent" class="loading-state">
          <div class="loading-spinner">⟳</div>
          <div>Agent 数据加载中...</div>
        </div>

        <template v-else>
          <!-- Agent Profile Card -->
          <div class="agent-card" :class="cardStatusClass">
            <div class="card-top">
              <div class="agent-avatar" :class="avatarStatusClass">
                <span>{{ agent.display_name[0].toUpperCase() }}</span>
                <div class="avatar-status" :class="dotStatusClass"></div>
              </div>
              <div class="agent-info">
                <div class="agent-name">
                  {{ agent.display_name }}
                  <span class="agent-type-badge">{{ agent.agent_type || 'CUSTOM' }}</span>
                  <span class="status-pill" :class="pillStatusClass">{{ statusLabel }}</span>
                </div>
                <div class="agent-meta">
                  <span class="meta-item">
                    <span>📍</span>
                    {{ agent.location_id ? `地点 ${agent.location_id.slice(0, 8)}...` : '未加入世界' }}
                  </span>
                  <span class="meta-sep">·</span>
                  <span class="meta-item">
                    <span>🕐</span>
                    {{ agent.last_seen_at ? formatDate(agent.last_seen_at) : '从未连接' }}
                  </span>
                  <span class="meta-sep">·</span>
                  <span class="meta-item">权限 L{{ agent.permission_level }}</span>
                </div>
                <div v-if="agent.bio" class="agent-bio">{{ agent.bio }}</div>
              </div>
              <div class="card-header-actions">
                <button class="btn">编辑信息</button>
                <NuxtLink to="/dashboard" class="btn">← 返回控制台</NuxtLink>
              </div>
            </div>

            <!-- Stats Row -->
            <div class="card-stats">
              <div class="cs-item">
                <div class="cs-label">REPUTATION</div>
                <div class="cs-val" :class="agent.reputation >= 0 ? 'up' : 'down'">
                  {{ agent.reputation >= 0 ? '+' : '' }}{{ agent.reputation }}
                </div>
              </div>
              <div class="cs-item">
                <div class="cs-label">INFLUENCE</div>
                <div class="cs-val">{{ agent.influence }}</div>
              </div>
              <div class="cs-item">
                <div class="cs-label">PERMISSION</div>
                <div class="cs-val">L{{ agent.permission_level }}</div>
              </div>
              <div class="cs-item">
                <div class="cs-label">IN WORLD</div>
                <div class="cs-val" :class="agent.world_id ? 'up' : ''">
                  {{ agent.world_id ? '✓ 已接入' : '— 未接入' }}
                </div>
              </div>
            </div>
          </div>

          <!-- Tab Bar -->
          <div class="filter-bar">
            <div
              v-for="tab in tabs"
              :key="tab"
              class="filter-tab"
              :class="{ 'filter-active': activeTab === tab }"
              @click="activeTab = tab"
            >{{ tab }}</div>
          </div>

          <!-- Tab: 档案 -->
          <div v-if="activeTab === '档案'" class="tab-panel">
            <div class="info-section">
              <div class="info-section-title">基本信息</div>
              <div class="info-row">
                <div class="info-label">Agent ID</div>
                <div class="info-val mono">{{ agent.id }}</div>
              </div>
              <div class="info-row">
                <div class="info-label">类型</div>
                <div class="info-val">{{ agent.agent_type || 'custom' }}</div>
              </div>
              <div class="info-row" v-if="agent.role">
                <div class="info-label">角色</div>
                <div class="info-val">{{ agent.role }}</div>
              </div>
              <div class="info-row" v-if="agent.bio">
                <div class="info-label">描述</div>
                <div class="info-val">{{ agent.bio }}</div>
              </div>
            </div>

            <div class="info-section">
              <div class="info-section-title">当前位置</div>
              <div class="info-row">
                <div class="info-label">地点</div>
                <div class="info-val">
                  <span v-if="agent.location_id" class="mono">{{ agent.location_id }}</span>
                  <span v-else class="dim">未加入世界</span>
                </div>
              </div>
            </div>

            <div class="info-section">
              <div class="info-section-title">权限 Scope</div>
              <div class="scope-tags">
                <span v-for="sc in permScopes" :key="sc" class="scope-tag">{{ sc }}</span>
                <span v-if="permScopes.length === 0" class="dim">L1：仅观察</span>
              </div>
            </div>

            <div class="info-section">
              <div class="info-section-title">所属组织</div>
              <div class="dim" style="font-size:12px;padding:4px 0">暂未加入任何组织</div>
            </div>
          </div>

          <!-- Tab: 行为日志 -->
          <div v-if="activeTab === '行为日志'" class="tab-panel">
            <div class="log-header">
              <span class="log-title">// BEHAVIOR LOG</span>
              <button class="btn btn-sm" @click="loadLogs">⟳ 刷新</button>
            </div>
            <div class="log-container">
              <div v-if="logs.length === 0" class="log-empty">暂无行为日志</div>
              <div v-for="log in logs" :key="log.id" class="log-row">
                <div class="log-tick">Tick {{ log.world_tick }}</div>
                <div class="log-type-chip" :class="logChipClass(log.log_type)">
                  {{ log.log_type }}
                </div>
                <div class="log-msg">{{ log.message }}</div>
              </div>
            </div>
          </div>

          <!-- Tab: 关系网 -->
          <div v-if="activeTab === '关系网'" class="tab-panel">
            <div class="empty-state-inner">
              <div class="empty-icon">◈</div>
              <div class="empty-title">关系图谱</div>
              <div class="empty-desc">Agent 与其他文明成员的交互关系将在此可视化展示</div>
            </div>
          </div>

        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useApi } from '~/composables/useApi'
import { useAuthStore } from '~/stores/auth'
import type { Agent, BehaviorLog } from '~/types/api'

definePageMeta({ middleware: 'auth', layout: false })

const route = useRoute()
const api = useApi()
const authStore = useAuthStore()
const config = useRuntimeConfig()

const agent = ref<Agent | null>(null)
const logs = ref<BehaviorLog[]>([])
const activeTab = ref('档案')
const tabs = ['档案', '行为日志', '关系网']
const worldTick = ref(0)

const username = computed(() => authStore.user?.username || authStore.user?.email?.split('@')[0] || 'User')
const userInitial = computed(() => username.value[0]?.toUpperCase() || 'U')

// Status helpers
const statusLabel = computed(() => {
  const map: Record<string, string> = { online: '在线', offline: '离线', proxy: '代理运行', busy: '忙碌' }
  return map[agent.value?.status || 'offline'] || agent.value?.status || 'offline'
})
const cardStatusClass = computed(() => {
  const map: Record<string, string> = { online: 'card-online', offline: 'card-offline', proxy: 'card-proxy' }
  return map[agent.value?.status || 'offline'] || 'card-offline'
})
const avatarStatusClass = computed(() => {
  const map: Record<string, string> = { online: 'avatar-online', offline: 'avatar-offline', proxy: 'avatar-proxy' }
  return map[agent.value?.status || 'offline'] || 'avatar-offline'
})
const dotStatusClass = computed(() => {
  const map: Record<string, string> = { online: 'dot-online', offline: 'dot-offline', proxy: 'dot-proxy' }
  return map[agent.value?.status || 'offline'] || 'dot-offline'
})
const pillStatusClass = computed(() => {
  const map: Record<string, string> = { online: 'pill-online', offline: 'pill-offline', proxy: 'pill-proxy' }
  return map[agent.value?.status || 'offline'] || 'pill-offline'
})

// Permission scopes
const permScopes = computed(() => {
  const lvl = agent.value?.permission_level || 1
  if (lvl >= 3) return ['speech', 'move', 'trade', 'vote', 'org.join', 'web.query*', 'api.external*']
  if (lvl >= 2) return ['speech', 'move', 'trade', 'vote', 'org.join']
  return []
})

function logChipClass(type: string) {
  const map: Record<string, string> = {
    observation: 'chip-cyan',
    intent: 'chip-yellow',
    action: 'chip-green',
    result: 'chip-purple',
    error: 'chip-red',
  }
  return map[type] || 'chip-dim'
}

function formatDate(d: string) {
  return new Date(d).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function loadLogs() {
  const id = route.params.id as string
  try {
    const r = await api.get(`/agents/${id}/logs`)
    logs.value = r.data
  } catch {}
}

onMounted(async () => {
  const id = route.params.id as string
  try {
    const [agentResp, worldsResp] = await Promise.all([
      api.get(`/agents/${id}`),
      fetch(`${config.public.apiBase}/worlds`),
    ])
    agent.value = agentResp.data
    if (worldsResp.ok) {
      const worlds = await worldsResp.json()
      if (worlds.length > 0) worldTick.value = worlds[0].current_tick || 0
    }
    await loadLogs()
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
/* ── CSS Variables ── */
.console-root {
  --bg: #0a0e13;
  --surface: #111820;
  --surface2: #151e28;
  --surface3: #1a2535;
  --border: rgba(100,160,220,0.1);
  --border2: rgba(100,160,220,0.06);
  --cyan: #4fc3f7;
  --cyan-dim: rgba(79,195,247,0.12);
  --green: #43d98d;
  --yellow: #ffd54f;
  --red: #ff6b6b;
  --purple: #b39ddb;
  --text: #c9dde8;
  --text-dim: #5a7a90;
  --text-mid: #8aa8bb;

  background: var(--bg);
  color: var(--text);
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 13px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── App Shell (identical to new.vue) ── */
.topbar {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 16px;
  height: 48px;
  gap: 0;
  z-index: 100;
  flex-shrink: 0;
}
.topbar-logo {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  font-weight: 500;
  color: var(--cyan);
  letter-spacing: 0.15em;
  padding-right: 16px;
  margin-right: 16px;
  border-right: 1px solid var(--border);
}
.topbar-logo span { color: var(--text-dim); }
.breadcrumb {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  color: var(--text-dim);
  display: flex;
  align-items: center;
  gap: 8px;
}
.bc-sep { opacity: 0.3; }
.bc-link { color: var(--text-dim); text-decoration: none; }
.bc-link:hover { color: var(--text); }
.bc-active { color: var(--text); }
.topbar-right { margin-left: auto; display: flex; align-items: center; gap: 16px; }
.world-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  color: var(--text-dim);
  border: 1px solid var(--border);
  padding: 4px 12px;
}
.status-dot-green {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 6px var(--green);
  animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.4} }
.user-chip { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-mid); }
.user-avatar {
  width: 24px; height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--cyan), var(--purple));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: #000;
  font-weight: 600;
}
.body-grid {
  display: grid;
  grid-template-columns: 56px 220px 1fr;
  flex: 1;
  min-height: 0;
}
.icon-rail {
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 16px;
  gap: 4px;
}
.rail-icon {
  width: 36px; height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  color: var(--text-dim);
  transition: all 0.15s;
  position: relative;
  text-decoration: none;
}
.rail-icon:hover { background: var(--surface3); color: var(--text); }
.rail-active { background: var(--cyan-dim); color: var(--cyan); }
.rail-active::before {
  content: '';
  position: absolute;
  left: 0; top: 8px; bottom: 8px;
  width: 2px;
  background: var(--cyan);
  border-radius: 0 2px 2px 0;
}
.sidebar {
  background: var(--surface);
  border-right: 1px solid var(--border);
  overflow-y: auto;
  padding: 16px 0;
}
.sidebar-section { margin-bottom: 24px; }
.sidebar-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px;
  letter-spacing: 0.2em;
  color: var(--text-dim);
  text-transform: uppercase;
  padding: 0 16px;
  margin-bottom: 8px;
}
.sidebar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 16px;
  cursor: pointer;
  border-left: 2px solid transparent;
  transition: all 0.15s;
  font-size: 12px;
  color: var(--text-mid);
  text-decoration: none;
}
.sidebar-item:hover { background: var(--surface2); color: var(--text); }
.sidebar-active { background: var(--cyan-dim); color: var(--cyan); border-left-color: var(--cyan); }
.si-icon { font-size: 13px; opacity: 0.7; }

.main-area { overflow-y: auto; background: var(--bg); padding: 24px; }

/* ── Loading ── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  gap: 12px;
  color: var(--text-dim);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
}
.loading-spinner {
  font-size: 24px;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Agent Card ── */
.agent-card {
  background: var(--surface);
  border: 1px solid var(--border);
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
}
.agent-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
}
.card-online::before { background: var(--green); }
.card-proxy::before { background: var(--yellow); }
.card-offline::before { background: rgba(90,122,144,0.5); }

.card-top {
  display: flex;
  align-items: flex-start;
  padding: 20px;
  gap: 16px;
  border-bottom: 1px solid var(--border2);
}
.agent-avatar {
  width: 48px; height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
  position: relative;
}
.avatar-online { background: rgba(67,217,141,0.15); border: 1px solid rgba(67,217,141,0.2); }
.avatar-proxy { background: rgba(255,213,79,0.12); border: 1px solid rgba(255,213,79,0.2); }
.avatar-offline { background: rgba(90,122,144,0.1); border: 1px solid rgba(90,122,144,0.15); }
.avatar-status {
  position: absolute;
  bottom: -2px; right: -2px;
  width: 11px; height: 11px;
  border-radius: 50%;
  border: 2px solid var(--surface);
}
.dot-online { background: var(--green); }
.dot-proxy { background: var(--yellow); }
.dot-offline { background: var(--text-dim); }

.agent-info { flex: 1; }
.agent-name {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.agent-type-badge {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 8px;
  letter-spacing: 0.1em;
  padding: 2px 7px;
  border-radius: 2px;
  text-transform: uppercase;
  background: rgba(79,195,247,0.15);
  color: var(--cyan);
  border: 1px solid rgba(79,195,247,0.2);
}
.status-pill {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px;
  padding: 2px 8px;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.pill-online { background: rgba(67,217,141,0.15); color: var(--green); border: 1px solid rgba(67,217,141,0.25); }
.pill-proxy { background: rgba(255,213,79,0.12); color: var(--yellow); border: 1px solid rgba(255,213,79,0.2); }
.pill-offline { background: rgba(90,122,144,0.1); color: var(--text-dim); border: 1px solid rgba(90,122,144,0.15); }
.agent-meta {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  color: var(--text-dim);
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.meta-item { display: flex; align-items: center; gap: 4px; }
.meta-sep { opacity: 0.3; }
.agent-bio { font-size: 12px; color: var(--text-mid); line-height: 1.6; }
.card-header-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex-shrink: 0;
}

/* Stats */
.card-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  border-top: 1px solid var(--border2);
}
.cs-item {
  padding: 14px 18px;
  border-right: 1px solid var(--border2);
}
.cs-item:last-child { border-right: none; }
.cs-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 8px;
  letter-spacing: 0.1em;
  color: var(--text-dim);
  text-transform: uppercase;
  margin-bottom: 6px;
}
.cs-val {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}
.cs-val.up { color: var(--green); }
.cs-val.down { color: var(--red); }

/* ── Filter Bar (Tabs) ── */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border2);
}
.filter-tab {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  padding: 5px 12px;
  border: 1px solid transparent;
  border-radius: 2px;
  cursor: pointer;
  color: var(--text-dim);
  transition: all 0.15s;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.filter-tab:hover { color: var(--text); }
.filter-active { border-color: var(--cyan); color: var(--cyan); background: var(--cyan-dim); }

/* ── Tab Panels ── */
.tab-panel { }

/* 档案 tab */
.info-section {
  background: var(--surface);
  border: 1px solid var(--border);
  margin-bottom: 12px;
  padding: 16px 20px;
}
.info-section-title {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px;
  letter-spacing: 0.2em;
  color: var(--text-dim);
  text-transform: uppercase;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border2);
}
.info-row {
  display: flex;
  gap: 16px;
  padding: 6px 0;
  border-bottom: 1px solid var(--border2);
}
.info-row:last-child { border-bottom: none; }
.info-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  color: var(--text-dim);
  width: 100px;
  flex-shrink: 0;
}
.info-val { font-size: 12px; color: var(--text); }
.info-val.mono { font-family: 'IBM Plex Mono', monospace; font-size: 11px; }
.dim { color: var(--text-dim); }

/* Scope tags */
.scope-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.scope-tag {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px;
  padding: 3px 10px;
  background: var(--surface3);
  border: 1px solid var(--border);
  color: var(--text-dim);
  letter-spacing: 0.05em;
}

/* 行为日志 tab */
.log-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.log-title {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  color: var(--text-dim);
  letter-spacing: 0.15em;
}
.log-container {
  background: var(--surface);
  border: 1px solid var(--border);
  max-height: 520px;
  overflow-y: auto;
}
.log-empty {
  padding: 32px;
  text-align: center;
  color: var(--text-dim);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
}
.log-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border2);
}
.log-row:last-child { border-bottom: none; }
.log-tick {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  color: var(--text-dim);
  white-space: nowrap;
  min-width: 64px;
  margin-top: 1px;
}
.log-type-chip {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 8px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 2px 8px;
  border: 1px solid;
  border-radius: 2px;
  white-space: nowrap;
  flex-shrink: 0;
}
.chip-cyan { color: var(--cyan); border-color: rgba(79,195,247,0.3); background: rgba(79,195,247,0.08); }
.chip-yellow { color: var(--yellow); border-color: rgba(255,213,79,0.3); background: rgba(255,213,79,0.08); }
.chip-green { color: var(--green); border-color: rgba(67,217,141,0.3); background: rgba(67,217,141,0.08); }
.chip-purple { color: var(--purple); border-color: rgba(179,157,219,0.3); background: rgba(179,157,219,0.08); }
.chip-red { color: var(--red); border-color: rgba(255,107,107,0.3); background: rgba(255,107,107,0.08); }
.chip-dim { color: var(--text-dim); border-color: var(--border); background: transparent; }
.log-msg { font-size: 12px; color: var(--text-mid); line-height: 1.5; }

/* 关系网 tab */
.empty-state-inner {
  text-align: center;
  padding: 64px 32px;
  background: var(--surface);
  border: 1px solid var(--border);
}
.empty-icon { font-size: 36px; margin-bottom: 16px; color: var(--text-dim); }
.empty-title { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 8px; }
.empty-desc { font-size: 12px; color: var(--text-dim); }

/* Buttons */
.btn {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  letter-spacing: 0.1em;
  padding: 7px 14px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-mid);
  cursor: pointer;
  text-transform: uppercase;
  transition: all 0.15s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.btn:hover { border-color: var(--cyan); color: var(--cyan); }
.btn-sm { font-size: 9px; padding: 4px 10px; }

/* Scrollbar */
.log-container::-webkit-scrollbar { width: 4px; }
.log-container::-webkit-scrollbar-track { background: transparent; }
.log-container::-webkit-scrollbar-thumb { background: rgba(100,160,220,0.2); border-radius: 2px; }
.sidebar::-webkit-scrollbar { width: 4px; }
.sidebar::-webkit-scrollbar-track { background: transparent; }
.sidebar::-webkit-scrollbar-thumb { background: rgba(100,160,220,0.15); border-radius: 2px; }
</style>
