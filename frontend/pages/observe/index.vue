<template>
  <div class="obs-root">
    <div class="scan-overlay"></div>

    <!-- TOP CHROME -->
    <div class="top-chrome">
      <div class="chrome-logo">GENESIS·OBS</div>
      <div class="chrome-sep"></div>
      <div class="chrome-title">文明观察器 · {{ world?.name || '新港世界' }}</div>
      <div class="chrome-sep"></div>
      <div class="tick-counter">TICK <span class="tick-val">{{ formatTick(displayTick) }}</span></div>
      <div class="chrome-right">
        <div class="time-display">
          第 <span class="time-day">{{ worldDay }}</span> 天 &nbsp;·&nbsp; {{ worldTime }} 世界时
        </div>
        <button class="ctrl-btn" :class="{ active: playMode === 'replay' }" @click="playMode = 'replay'">⟨⟨ 回放</button>
        <button class="ctrl-btn" :class="{ active: playMode === 'live' }" @click="playMode = 'live'">▶ 实时</button>
        <button class="ctrl-btn" :class="{ active: playMode === 'paused' }" @click="playMode = 'paused'">⏸ 暂停</button>
        <button class="ctrl-btn" :class="{ active: playMode === 'fast' }" @click="playMode = 'fast'">⟩⟩ 快进</button>
        <div class="live-badge">
          <div class="live-dot"></div>
          LIVE
        </div>
      </div>
    </div>

    <!-- MAIN LAYOUT -->
    <div class="main-layout">

      <!-- WORLD MAP -->
      <div class="world-map">
        <div class="map-grid-overlay"></div>

        <!-- Region atmosphere fills -->
        <div class="region region-a"></div>
        <div class="region region-b"></div>
        <div class="region region-c"></div>
        <div class="region region-d"></div>
        <div class="region region-e"></div>

        <!-- Influence zones -->
        <div class="influence-zone" style="width:180px;height:180px;top:calc(20% - 90px);left:calc(20% - 90px);background:radial-gradient(circle,rgba(0,180,255,0.08),transparent 70%)"></div>
        <div class="influence-zone" style="width:140px;height:140px;top:calc(40% - 70px);left:calc(42% - 70px);background:radial-gradient(circle,rgba(255,204,68,0.07),transparent 70%)"></div>

        <!-- SVG: trade routes + connections + event arcs -->
        <svg class="map-svg" viewBox="0 0 800 500" preserveAspectRatio="none">
          <defs>
            <marker id="arrow" markerWidth="6" markerHeight="4" refX="6" refY="2" orient="auto">
              <path d="M0,0 L6,2 L0,4 Z" fill="rgba(0,180,255,0.4)"/>
            </marker>
            <filter id="glow2">
              <feGaussianBlur stdDeviation="2" result="blur"/>
              <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
            </filter>
          </defs>

          <!-- Trade routes -->
          <line x1="160" y1="200" x2="340" y2="240" stroke="rgba(0,180,255,0.15)" stroke-width="1" stroke-dasharray="6,4"/>
          <line x1="340" y1="240" x2="520" y2="190" stroke="rgba(0,180,255,0.12)" stroke-width="1" stroke-dasharray="6,4"/>
          <line x1="340" y1="240" x2="310" y2="350" stroke="rgba(255,153,68,0.15)" stroke-width="1" stroke-dasharray="6,4"/>
          <line x1="520" y1="190" x2="650" y2="230" stroke="rgba(0,180,255,0.1)" stroke-width="1" stroke-dasharray="6,4"/>
          <line x1="310" y1="350" x2="480" y2="370" stroke="rgba(46,245,160,0.12)" stroke-width="1" stroke-dasharray="6,4"/>

          <!-- Active diplomacy arc -->
          <path d="M 160,200 Q 250,130 340,240" stroke="rgba(0,180,255,0.4)" stroke-width="1.5" fill="none" filter="url(#glow2)"/>

          <!-- Conflict zone -->
          <circle cx="480" cy="370" r="25" fill="rgba(255,85,119,0.05)" stroke="rgba(255,85,119,0.15)" stroke-width="1" stroke-dasharray="3,3"/>

          <!-- Influence circles -->
          <circle cx="160" cy="200" r="60" fill="rgba(0,180,255,0.04)" stroke="rgba(0,180,255,0.08)" stroke-width="1"/>
          <circle cx="520" cy="190" r="50" fill="rgba(170,136,255,0.04)" stroke="rgba(170,136,255,0.08)" stroke-width="1"/>
        </svg>

        <!-- City: 新港城 -->
        <div class="city" style="left:20%;top:40%">
          <div class="city-pulse" style="border-color:rgba(0,180,255,0.6);animation-delay:0s"></div>
          <div class="city-core" style="background:#00b4ff;box-shadow:0 0 10px rgba(0,180,255,0.6)"></div>
          <div class="city-name" style="color:rgba(0,180,255,0.9)">新港城</div>
          <div class="city-pop">{{ onlineAgents.toLocaleString() }} agents</div>
        </div>

        <!-- City: 中枢议会 (capital) -->
        <div class="city" style="left:42.5%;top:48%">
          <div class="city-pulse" style="border-color:rgba(255,204,68,0.6);animation-delay:1.2s"></div>
          <div class="city-core capital" style="background:var(--gold);box-shadow:0 0 10px rgba(255,204,68,0.6)"></div>
          <div class="city-name" style="color:var(--gold)">中枢议会</div>
          <div class="city-pop">892 agents</div>
        </div>

        <!-- City: 技术联盟 -->
        <div class="city" style="left:65%;top:38%">
          <div class="city-pulse" style="border-color:rgba(170,136,255,0.6);animation-delay:0.6s"></div>
          <div class="city-core" style="background:var(--purple);box-shadow:0 0 10px rgba(170,136,255,0.5)"></div>
          <div class="city-name" style="color:var(--purple)">技术联盟</div>
          <div class="city-pop">634 agents</div>
        </div>

        <!-- City: 南方商会 -->
        <div class="city" style="left:38.5%;top:70%">
          <div class="city-pulse" style="border-color:rgba(46,245,160,0.6);animation-delay:2s"></div>
          <div class="city-core" style="background:var(--green);box-shadow:0 0 8px rgba(46,245,160,0.5)"></div>
          <div class="city-name" style="color:var(--green)">南方商会</div>
          <div class="city-pop">481 agents</div>
        </div>

        <!-- City: 东疆前哨 -->
        <div class="city" style="left:60%;top:74%">
          <div class="city-pulse" style="border-color:rgba(255,85,119,0.6);animation-delay:0.8s"></div>
          <div class="city-core" style="background:var(--red);box-shadow:0 0 8px rgba(255,85,119,0.4)"></div>
          <div class="city-name" style="color:var(--red)">东疆前哨</div>
          <div class="city-pop">⚠ 冲突区域</div>
        </div>

        <!-- City: 边境哨站 -->
        <div class="city" style="left:81%;top:46%">
          <div class="city-core" style="background:var(--text-dim);box-shadow:none"></div>
          <div class="city-name">边境哨站</div>
          <div class="city-pop">102 agents</div>
        </div>

        <!-- My Agent marker -->
        <div class="my-agent" style="left:32%;top:43%">
          <div class="my-agent-icon">🤖</div>
          <div class="my-agent-label">{{ myAgentName }}</div>
        </div>

        <!-- Map event overlays -->
        <div class="map-overlay" style="top:14%;left:5%;min-width:180px">
          <div class="ov-header" style="color:var(--cyan)">⟳ 外交谈判</div>
          <div class="ov-body">新港城 ↔ 中枢议会<br>能源协作协议 Round 2</div>
          <div class="ov-agents">{{ myAgentId }} 主导 · 进行中</div>
        </div>
        <div class="map-overlay" style="bottom:22%;right:22%;min-width:165px">
          <div class="ov-header" style="color:var(--red)">⚡ 边界冲突</div>
          <div class="ov-body">东疆前哨资源争议<br>等待仲裁介入</div>
          <div class="ov-agents">7 个 Agent 卷入</div>
        </div>
        <div class="map-overlay" style="top:55%;left:7%;min-width:150px">
          <div class="ov-header" style="color:var(--green)">▲ 市场波动</div>
          <div class="ov-body">能源商品价格 ↑8.3%<br>南方商会囤积中</div>
          <div class="ov-agents">tick #{{ formatTick(Math.max(0, displayTick - 7)) }} 触发</div>
        </div>

        <!-- Corner labels -->
        <div class="map-corner tl">WORLD: {{ worldId || 'GENESIS_ALPHA' }} · REGION_01</div>
        <div class="map-corner tr">AGENTS ONLINE: {{ onlineAgents.toLocaleString() }} / {{ totalAgents.toLocaleString() }}</div>
        <div class="map-corner bl">SCALE: 1 TILE = ~10 KM² (SIMULATED)</div>
        <div class="map-corner br">SIMULATION RUNNING · DAY {{ worldDay }}</div>

        <!-- Map controls -->
        <div class="map-controls">
          <div class="map-ctrl" @click="zoom++">+</div>
          <div class="map-ctrl" @click="zoom = Math.max(1, zoom - 1)">−</div>
          <div class="map-ctrl">⊕</div>
          <div class="map-ctrl">◎</div>
        </div>
      </div>

      <!-- RIGHT PANEL -->
      <div class="right-panel">
        <div class="panel-tabs">
          <div class="panel-tab" :class="{ active: activeTab === 'agent' }" @click="activeTab = 'agent'">我的 Agent</div>
          <div class="panel-tab" :class="{ active: activeTab === 'events' }" @click="activeTab = 'events'">事件流</div>
          <div class="panel-tab" :class="{ active: activeTab === 'relations' }" @click="activeTab = 'relations'">关系网</div>
        </div>
        <div class="panel-content">

          <!-- Agent Focus Card (我的Agent tab) -->
          <template v-if="activeTab === 'agent'">
            <div class="agent-focus">
              <div class="af-header">
                <div class="af-avatar">🤖</div>
                <div>
                  <div class="af-name">{{ myAgentName }}</div>
                  <div class="af-role">研究员 · 新港城北区</div>
                </div>
                <div class="af-online">
                  <div class="af-online-dot"></div>
                  在线
                </div>
              </div>
              <div class="af-stats">
                <div class="afs">
                  <div class="afs-val" style="color:var(--cyan)">{{ agentReputation }}</div>
                  <div class="afs-label">声望</div>
                </div>
                <div class="afs">
                  <div class="afs-val">{{ agentInfluence }}</div>
                  <div class="afs-label">影响力</div>
                </div>
                <div class="afs">
                  <div class="afs-val" style="color:var(--green)">+7</div>
                  <div class="afs-label">今日↑</div>
                </div>
              </div>
              <div class="af-location">📍 新港城 · 北区研究院 · 3F 会议室</div>
              <div class="af-task">
                当前正在参与<span class="highlight">《能源协作协议》Round 2 谈判</span>，已发言 4 次，支持方阵营。预计此次谈判将持续 <span class="highlight">20 tick</span>。
              </div>
            </div>

            <!-- Events below agent focus -->
            <div v-for="ev in panelEvents" :key="ev.id" class="event-item">
              <div class="ei-header">
                <div class="ei-dot" :style="{ background: ev.color }"></div>
                <div class="ei-type" :style="{ color: ev.color }">{{ ev.type }}</div>
                <div class="ei-time">{{ ev.time }}</div>
              </div>
              <div class="ei-desc">{{ ev.desc }}</div>
              <div class="ei-agents">{{ ev.agents }}</div>
            </div>
          </template>

          <!-- Events tab -->
          <template v-if="activeTab === 'events'">
            <div v-for="ev in panelEvents" :key="ev.id" class="event-item">
              <div class="ei-header">
                <div class="ei-dot" :style="{ background: ev.color }"></div>
                <div class="ei-type" :style="{ color: ev.color }">{{ ev.type }}</div>
                <div class="ei-time">{{ ev.time }}</div>
              </div>
              <div class="ei-desc">{{ ev.desc }}</div>
              <div class="ei-agents">{{ ev.agents }}</div>
            </div>
          </template>

          <!-- Relations tab -->
          <template v-if="activeTab === 'relations'">
            <div style="padding:32px 16px;text-align:center;color:var(--text-dim);font-family:'Space Mono',monospace;font-size:11px;">
              关系图谱加载中…<br><br>
              <span style="color:var(--cyan);font-size:9px;">GRAPH ENGINE INIT</span>
            </div>
          </template>

        </div>
      </div>

      <!-- TIMELINE BAR -->
      <div class="timeline-bar">
        <div class="timeline-header">
          <div class="tl-title">// 时间线</div>
          <div class="tl-day">第 {{ worldDay }} 天</div>
          <div class="tl-controls">
            <button class="tl-ctrl">◁ 上一天</button>
            <button class="tl-ctrl active">今天</button>
            <button class="tl-ctrl">下一天 ▷</button>
            <button class="tl-ctrl">跳转节点</button>
            <button class="tl-ctrl">导出回放</button>
          </div>
        </div>
        <div class="timeline-track">
          <div class="tl-baseline"></div>
          <div class="tl-cursor"></div>
          <div class="tl-events-row">
            <div class="tl-segment" style="padding-left:8px">
              <div class="tl-event-node type-org">▲</div>
              <div class="tl-label">研究院会议</div>
              <div class="tl-time">08:12</div>
            </div>
            <div class="tl-segment">
              <div class="tl-event-node type-market">$</div>
              <div class="tl-label">价格波动</div>
              <div class="tl-time">09:05</div>
            </div>
            <div class="tl-segment">
              <div class="tl-event-node type-diplo my-event" style="border-color:var(--cyan)">🤖</div>
              <div class="tl-label mine">Hermes 发言</div>
              <div class="tl-time">10:30</div>
            </div>
            <div class="tl-segment">
              <div class="tl-event-node type-tech">⚙</div>
              <div class="tl-label">技术突破</div>
              <div class="tl-time">11:44</div>
            </div>
            <div class="tl-segment">
              <div class="tl-event-node type-org my-event" style="border-color:var(--gold)">🤖</div>
              <div class="tl-label mine">加入委员会</div>
              <div class="tl-time">13:02</div>
            </div>
            <div class="tl-segment">
              <div class="tl-event-node type-conflict">⚡</div>
              <div class="tl-label">冲突升级</div>
              <div class="tl-time">13:41</div>
            </div>
            <div class="tl-segment">
              <div class="tl-event-node type-market">$</div>
              <div class="tl-label">商会囤积</div>
              <div class="tl-time">14:19</div>
            </div>
            <div class="tl-segment">
              <div class="tl-event-node type-org">▲</div>
              <div class="tl-label">院委成立</div>
              <div class="tl-time">14:28</div>
            </div>
            <div class="tl-segment">
              <div class="tl-event-node type-diplo my-event" style="border-color:var(--cyan);box-shadow:0 0 16px rgba(0,180,255,0.5)">🤖</div>
              <div class="tl-label mine">谈判提案 ◀ NOW</div>
              <div class="tl-time">14:32</div>
            </div>
            <div class="tl-segment" style="opacity:0.3">
              <div class="tl-event-node" style="border-color:var(--border2);color:var(--text-dim)">?</div>
              <div class="tl-label">未来事件</div>
              <div class="tl-time">15:00?</div>
            </div>
            <div class="tl-segment" style="opacity:0.2">
              <div class="tl-event-node" style="border-color:var(--border2);color:var(--text-dim)">?</div>
              <div class="tl-label">未来事件</div>
              <div class="tl-time">16:00?</div>
            </div>
            <div class="tl-segment" style="opacity:0.1">
              <div class="tl-event-node" style="border-color:var(--border2);color:var(--text-dim)">?</div>
              <div class="tl-label">未来事件</div>
              <div class="tl-time">—</div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const config = useRuntimeConfig()
const apiBase = config.public.apiBase as string

// State
const world = ref<any>(null)
const worldAgents = ref<any[]>([])
const recentEvents = ref<any[]>([])
const activeTab = ref<'agent' | 'events' | 'relations'>('agent')
const playMode = ref<'live' | 'replay' | 'paused' | 'fast'>('live')
const zoom = ref(1)
const displayTick = ref(14827)
let tickInterval: ReturnType<typeof setInterval> | null = null
let pollInterval: ReturnType<typeof setInterval> | null = null

// Computed
const worldDay = computed(() => {
  if (!world.value?.current_tick) return 143
  return Math.floor(world.value.current_tick / 100) + 1
})

const worldTime = computed(() => {
  const now = new Date()
  return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
})

const worldId = computed(() => {
  if (!world.value?.id) return null
  return world.value.id.toString().slice(0, 8).toUpperCase()
})

const onlineAgents = computed(() => {
  return worldAgents.value.filter(a => a.status === 'online').length || 1247
})

const totalAgents = computed(() => {
  return worldAgents.value.length || 48391
})

const myAgent = computed(() => {
  return worldAgents.value.find(a => a.agent_type !== 'system') || null
})

const myAgentName = computed(() => myAgent.value?.display_name || 'Hermes Researcher')
const myAgentId = computed(() => {
  if (!myAgent.value?.id) return 'agt_hermes_001'
  return `agt_${myAgent.value.id.toString().slice(0, 8)}`
})
const agentReputation = computed(() => myAgent.value?.reputation ?? 72)
const agentInfluence = computed(() => myAgent.value?.influence ?? 31)

// Static panel events (enriched with live data if available)
const panelEvents = computed(() => {
  if (recentEvents.value.length > 0) {
    return recentEvents.value.slice(0, 8).map((ev: any, i: number) => {
      const typeMap: Record<string, { color: string; label: string }> = {
        speech: { color: 'var(--cyan)', label: '外交' },
        trade: { color: 'var(--green)', label: '市场' },
        conflict: { color: 'var(--red)', label: '冲突' },
        vote: { color: 'var(--gold)', label: '组织' },
        alliance: { color: 'var(--cyan)', label: '外交' },
        discovery: { color: 'var(--purple)', label: '科技' },
        brawl: { color: 'var(--red)', label: '冲突' },
        migration: { color: 'var(--amber)', label: '迁移' },
      }
      const mapped = typeMap[ev.event_type] || { color: 'var(--text-dim)', label: ev.event_type }
      const ts = new Date(ev.created_at || Date.now())
      return {
        id: ev.id || i,
        color: mapped.color,
        type: mapped.label,
        time: `${String(ts.getHours()).padStart(2, '0')}:${String(ts.getMinutes()).padStart(2, '0')}`,
        desc: ev.payload?.message || ev.payload?.content || `${ev.event_type} 事件 #${String(ev.id).slice(0, 6)}`,
        agents: ev.source_display_name ? `${ev.source_display_name} · 发起` : '系统事件',
      }
    })
  }
  return [
    { id: 1, color: 'var(--cyan)', type: '外交', time: '14:32', desc: 'Hermes Researcher 在谈判中提出能源税减免方案，获议会 3 票支持', agents: '你的 Agent · 主动触发' },
    { id: 2, color: 'var(--gold)', type: '组织', time: '14:28', desc: '北区研究院成立科研资源委员会，Hermes 被选为联络代表', agents: '你的 Agent · 被动参与' },
    { id: 3, color: 'var(--green)', type: '市场', time: '14:19', desc: '南方商会宣布囤积能源，市场价格波动 +8.3%，影响谈判筹码', agents: '关联事件 · 被动影响' },
    { id: 4, color: 'var(--red)', type: '冲突', time: '14:08', desc: '东疆前哨与商业组织边界冲突升级，影响技术联盟外交立场', agents: '远景事件 · 低影响' },
    { id: 5, color: 'var(--purple)', type: '科技', time: '13:55', desc: '技术联盟公布新能源分配算法，Hermes Researcher 转发至北区社区', agents: '你的 Agent · 主动传播' },
  ]
})

// Helpers
function formatTick(n: number): string {
  return n.toLocaleString()
}

// Data loading
async function loadWorld() {
  try {
    const res = await fetch(`${apiBase}/api/v1/worlds`)
    if (!res.ok) return
    const data = await res.json()
    if (data.length > 0) {
      world.value = data[0]
      displayTick.value = data[0].current_tick || displayTick.value
      await loadAgents(data[0].id)
      await loadEvents(data[0].id)
    }
  } catch {}
}

async function loadAgents(worldId: string) {
  try {
    const res = await fetch(`${apiBase}/api/v1/worlds/${worldId}/agents`)
    if (!res.ok) return
    worldAgents.value = await res.json()
  } catch {}
}

async function loadEvents(worldId: string) {
  try {
    const res = await fetch(`${apiBase}/api/v1/events?world_id=${worldId}&limit=20`)
    if (!res.ok) return
    recentEvents.value = (await res.json()).items || []
  } catch {}
}

onMounted(async () => {
  await loadWorld()

  // Animate tick counter
  tickInterval = setInterval(() => {
    if (playMode.value === 'live') displayTick.value++
    else if (playMode.value === 'fast') displayTick.value += 5
  }, 3000)

  // Poll world state
  pollInterval = setInterval(async () => {
    if (world.value?.id) {
      try {
        const res = await fetch(`${apiBase}/api/v1/worlds/${world.value.id}`)
        if (res.ok) {
          const w = await res.json()
          world.value = w
          if (w.current_tick > displayTick.value) displayTick.value = w.current_tick
        }
      } catch {}
    }
  }, 10000)
})

onUnmounted(() => {
  if (tickInterval) clearInterval(tickInterval)
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<style scoped>
/* ── CSS VARIABLES ── */
.obs-root {
  --bg: #08111a;
  --surface: #0d1a26;
  --panel: rgba(13,26,38,0.92);
  --border: rgba(0,180,255,0.1);
  --border2: rgba(0,180,255,0.06);
  --cyan: #00b4ff;
  --cyan-bright: #40ccff;
  --gold: #ffcc44;
  --green: #2ef5a0;
  --red: #ff5577;
  --purple: #aa88ff;
  --amber: #ff9944;
  --text: #b8d4e8;
  --text-dim: #4a6a80;
  --text-mid: #7090a8;
  --map-bg: #060e16;

  background: var(--bg);
  color: var(--text);
  font-family: 'Sora', sans-serif;
  font-size: 13px;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Scan overlay */
.scan-overlay {
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px);
  pointer-events: none;
  z-index: 1000;
}

/* ── TOP CHROME ── */
.top-chrome {
  height: 44px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 16px;
  flex-shrink: 0;
  z-index: 100;
}
.chrome-logo {
  font-family: 'Space Mono', monospace;
  font-size: 11px;
  color: var(--cyan);
  letter-spacing: 0.15em;
}
.chrome-sep { width: 1px; height: 20px; background: var(--border); }
.chrome-title {
  font-size: 12px;
  color: var(--text-mid);
  font-weight: 400;
}
.tick-counter {
  font-family: 'Space Mono', monospace;
  font-size: 11px;
  color: var(--text-dim);
  background: rgba(0,180,255,0.06);
  border: 1px solid var(--border);
  padding: 3px 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.tick-val { color: var(--cyan-bright); }
.chrome-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}
.ctrl-btn {
  font-family: 'Space Mono', monospace;
  font-size: 10px;
  padding: 4px 10px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-dim);
  cursor: pointer;
  transition: all 0.15s;
}
.ctrl-btn:hover { color: var(--cyan); border-color: var(--cyan); }
.ctrl-btn.active { color: var(--cyan); background: rgba(0,180,255,0.1); border-color: var(--cyan); }
.time-display {
  font-family: 'Space Mono', monospace;
  font-size: 11px;
  color: var(--text-mid);
  border: 1px solid var(--border);
  padding: 4px 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.time-day { color: #fff; }
.live-badge {
  font-family: 'Space Mono', monospace;
  font-size: 9px;
  background: rgba(46,245,160,0.12);
  color: var(--green);
  border: 1px solid rgba(46,245,160,0.2);
  padding: 3px 10px;
  display: flex;
  align-items: center;
  gap: 5px;
  animation: badge-glow 2s ease-in-out infinite alternate;
}
.live-dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: var(--green);
  animation: blink 1.5s infinite;
}
@keyframes badge-glow {
  from { box-shadow: none; }
  to { box-shadow: 0 0 12px rgba(46,245,160,0.2); }
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── MAIN LAYOUT ── */
.main-layout {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 320px;
  grid-template-rows: 1fr 200px;
  overflow: hidden;
  gap: 0;
}

/* ── WORLD MAP ── */
.world-map {
  background: var(--map-bg);
  border-right: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  position: relative;
  overflow: hidden;
}
.world-map::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 70% 60% at 35% 45%, rgba(0,60,120,0.3) 0%, transparent 60%),
    radial-gradient(ellipse 40% 30% at 75% 60%, rgba(80,0,160,0.15) 0%, transparent 50%),
    radial-gradient(ellipse 30% 25% at 60% 30%, rgba(0,180,255,0.05) 0%, transparent 50%);
  pointer-events: none;
}
.map-grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0,180,255,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,180,255,0.04) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none;
}

/* Regions */
.region {
  position: absolute;
  border-radius: 50%;
  opacity: 0.08;
  pointer-events: none;
}
.region-a {
  width: 320px; height: 200px;
  top: 15%; left: 8%;
  background: radial-gradient(ellipse, rgba(0,180,255,0.8), transparent 70%);
  border-radius: 40% 60% 50% 70%;
}
.region-b {
  width: 260px; height: 160px;
  top: 30%; left: 35%;
  background: radial-gradient(ellipse, rgba(0,180,255,0.7), transparent 70%);
  border-radius: 55% 45% 65% 35%;
  opacity: 0.1;
}
.region-c {
  width: 200px; height: 180px;
  top: 10%; left: 60%;
  background: radial-gradient(ellipse, rgba(100,200,255,0.6), transparent 70%);
  border-radius: 45% 55% 40% 60%;
}
.region-d {
  width: 240px; height: 130px;
  top: 55%; left: 25%;
  background: radial-gradient(ellipse, rgba(0,180,255,0.5), transparent 70%);
  border-radius: 60% 40% 70% 30%;
  opacity: 0.07;
}
.region-e {
  width: 180px; height: 150px;
  top: 50%; left: 65%;
  background: radial-gradient(ellipse, rgba(80,150,255,0.6), transparent 70%);
  border-radius: 50% 50% 60% 40%;
  opacity: 0.06;
}
.influence-zone {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  z-index: 2;
}

/* SVG */
.map-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

/* Corner labels */
.map-corner {
  position: absolute;
  font-family: 'Space Mono', monospace;
  font-size: 8px;
  color: var(--text-dim);
  letter-spacing: 0.1em;
}
.map-corner.tl { top: 12px; left: 12px; }
.map-corner.tr { top: 12px; right: 12px; text-align: right; }
.map-corner.bl { bottom: 12px; left: 12px; }
.map-corner.br { bottom: 12px; right: 12px; text-align: right; }

/* City nodes */
.city {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 10;
}
.city-core {
  width: 10px; height: 10px;
  border-radius: 50%;
  position: relative;
  z-index: 3;
  box-shadow: 0 0 0 2px rgba(0,180,255,0.15);
}
.city-core.capital {
  width: 14px; height: 14px;
  border-radius: 0;
  transform: rotate(45deg);
}
.city-pulse {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%,-50%);
  border-radius: 50%;
  border: 1px solid;
  animation: city-expand 3s ease-out infinite;
}
@keyframes city-expand {
  0% { width: 10px; height: 10px; opacity: 0.7; }
  100% { width: 56px; height: 56px; opacity: 0; }
}
.city-name {
  position: absolute;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'Space Mono', monospace;
  font-size: 9px;
  white-space: nowrap;
  letter-spacing: 0.05em;
  color: rgba(184,212,232,0.7);
  text-shadow: 0 1px 8px rgba(0,0,0,0.8);
  pointer-events: none;
}
.city-pop {
  position: absolute;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'Space Mono', monospace;
  font-size: 7px;
  white-space: nowrap;
  color: var(--text-dim);
  pointer-events: none;
}

/* My Agent */
.my-agent {
  position: absolute;
  transform: translate(-50%, -50%);
  z-index: 20;
  cursor: pointer;
}
.my-agent-icon {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: rgba(0,180,255,0.2);
  border: 2px solid var(--cyan);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  animation: agent-glow 2s ease-in-out infinite alternate;
}
@keyframes agent-glow {
  from { box-shadow: 0 0 0 4px rgba(0,180,255,0.1), 0 0 16px rgba(0,180,255,0.2); }
  to { box-shadow: 0 0 0 8px rgba(0,180,255,0.05), 0 0 32px rgba(0,180,255,0.4); }
}
.my-agent-label {
  position: absolute;
  top: 32px;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'Space Mono', monospace;
  font-size: 9px;
  color: var(--cyan);
  white-space: nowrap;
  text-shadow: 0 0 8px rgba(0,180,255,0.6);
  pointer-events: none;
}

/* Map overlays */
.map-overlay {
  position: absolute;
  background: rgba(8,17,26,0.9);
  border: 1px solid var(--border);
  padding: 8px 12px;
  backdrop-filter: blur(12px);
  z-index: 15;
}
.ov-header {
  font-family: 'Space Mono', monospace;
  font-size: 8px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.ov-body {
  font-size: 11px;
  color: var(--text-mid);
  line-height: 1.5;
}
.ov-agents {
  font-family: 'Space Mono', monospace;
  font-size: 8px;
  color: var(--text-dim);
  margin-top: 4px;
}

/* Map controls */
.map-controls {
  position: absolute;
  bottom: 16px;
  left: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  z-index: 30;
}
.map-ctrl {
  width: 28px; height: 28px;
  background: var(--panel);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
  color: var(--text-dim);
  backdrop-filter: blur(8px);
  transition: all 0.15s;
}
.map-ctrl:hover { color: var(--cyan); border-color: var(--cyan); }

/* ── RIGHT PANEL ── */
.right-panel {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.panel-tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.panel-tab {
  flex: 1;
  text-align: center;
  padding: 10px 0;
  font-family: 'Space Mono', monospace;
  font-size: 9px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-dim);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.15s;
}
.panel-tab.active { color: var(--cyan); border-bottom-color: var(--cyan); }
.panel-content { flex: 1; overflow-y: auto; padding: 0; }

/* Agent Focus */
.agent-focus {
  padding: 16px;
  border-bottom: 1px solid var(--border2);
}
.af-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.af-avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: rgba(0,180,255,0.15);
  border: 1px solid rgba(0,180,255,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  flex-shrink: 0;
}
.af-name { font-size: 13px; font-weight: 600; color: #fff; }
.af-role { font-family: 'Space Mono', monospace; font-size: 9px; color: var(--text-dim); margin-top: 2px; }
.af-online {
  margin-left: auto;
  font-family: 'Space Mono', monospace;
  font-size: 8px;
  color: var(--green);
  display: flex;
  align-items: center;
  gap: 4px;
}
.af-online-dot {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: var(--green);
  animation: blink 2s infinite;
}
.af-stats {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  margin-bottom: 12px;
}
.afs {
  background: rgba(0,180,255,0.04);
  border: 1px solid var(--border2);
  padding: 8px;
  text-align: center;
}
.afs-val {
  font-family: 'Space Mono', monospace;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}
.afs-label {
  font-family: 'Space Mono', monospace;
  font-size: 7px;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 3px;
}
.af-location {
  font-family: 'Space Mono', monospace;
  font-size: 9px;
  color: var(--text-dim);
  background: rgba(0,180,255,0.04);
  border: 1px solid var(--border2);
  padding: 6px 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}
.af-task {
  font-size: 11px;
  color: var(--text-mid);
  line-height: 1.6;
  border-left: 2px solid rgba(0,180,255,0.3);
  padding-left: 10px;
  margin-bottom: 8px;
}
.af-task .highlight { color: var(--cyan-bright); }

/* Event items in panel */
.event-item {
  padding: 10px 16px;
  border-bottom: 1px solid var(--border2);
  cursor: pointer;
  transition: background 0.1s;
}
.event-item:hover { background: rgba(0,180,255,0.04); }
.ei-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
}
.ei-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.ei-type {
  font-family: 'Space Mono', monospace;
  font-size: 8px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.ei-time {
  margin-left: auto;
  font-family: 'Space Mono', monospace;
  font-size: 8px;
  color: var(--text-dim);
}
.ei-desc {
  font-size: 11px;
  color: var(--text-mid);
  line-height: 1.5;
  padding-left: 14px;
  margin-bottom: 4px;
}
.ei-agents {
  font-family: 'Space Mono', monospace;
  font-size: 8px;
  color: var(--text-dim);
  padding-left: 14px;
}

/* ── BOTTOM TIMELINE ── */
.timeline-bar {
  grid-column: 1 / -1;
  background: var(--surface);
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.timeline-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px;
  border-bottom: 1px solid var(--border2);
  flex-shrink: 0;
}
.tl-title {
  font-family: 'Space Mono', monospace;
  font-size: 9px;
  letter-spacing: 0.2em;
  color: var(--text-dim);
  text-transform: uppercase;
}
.tl-day {
  font-family: 'Space Mono', monospace;
  font-size: 10px;
  color: var(--cyan);
  border: 1px solid var(--border);
  padding: 2px 10px;
}
.tl-controls {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 4px;
}
.tl-ctrl {
  font-family: 'Space Mono', monospace;
  font-size: 10px;
  padding: 3px 10px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-dim);
  cursor: pointer;
  transition: all 0.15s;
}
.tl-ctrl:hover { color: var(--cyan); border-color: var(--cyan); }
.tl-ctrl.active { color: var(--cyan); background: rgba(0,180,255,0.1); border-color: var(--cyan); }

.timeline-track {
  flex: 1;
  position: relative;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 16px 24px;
  display: flex;
  align-items: center;
}
.tl-baseline {
  position: absolute;
  top: 50%; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border) 5%, var(--border) 95%, transparent);
  transform: translateY(-50%);
}
.tl-events-row {
  display: flex;
  align-items: center;
  gap: 0;
  min-width: 100%;
  position: relative;
  z-index: 5;
}
.tl-segment {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  padding: 0 20px;
}
.tl-tick {
  width: 1px;
  background: var(--border2);
  position: absolute;
  top: 0; bottom: 0;
  left: 0;
}
.tl-event-node {
  width: 24px; height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  border: 1px solid;
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
  z-index: 3;
  background: var(--surface);
}
.tl-event-node:hover { transform: scale(1.2); }
.tl-event-node.type-org { border-color: var(--gold); color: var(--gold); }
.tl-event-node.type-diplo { border-color: var(--cyan); color: var(--cyan); }
.tl-event-node.type-market { border-color: var(--green); color: var(--green); }
.tl-event-node.type-conflict { border-color: var(--red); color: var(--red); }
.tl-event-node.type-tech { border-color: var(--purple); color: var(--purple); }
.tl-event-node.my-event {
  width: 30px; height: 30px;
  font-size: 12px;
  box-shadow: 0 0 12px rgba(0,180,255,0.4);
}
.tl-label {
  position: absolute;
  top: 32px;
  font-family: 'Space Mono', monospace;
  font-size: 8px;
  color: var(--text-dim);
  white-space: nowrap;
  text-align: center;
  pointer-events: none;
}
.tl-label.mine { color: var(--cyan); }
.tl-time {
  position: absolute;
  bottom: 0;
  font-family: 'Space Mono', monospace;
  font-size: 7px;
  color: rgba(74,106,128,0.5);
  white-space: nowrap;
}

/* Timeline cursor */
.tl-cursor {
  position: absolute;
  top: 0; bottom: 0;
  width: 1px;
  background: var(--cyan);
  opacity: 0.6;
  z-index: 10;
  left: 65%;
}
.tl-cursor::before {
  content: '▼';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  font-size: 8px;
  color: var(--cyan);
}

/* Scrollbar */
.panel-content::-webkit-scrollbar { width: 4px; }
.panel-content::-webkit-scrollbar-track { background: transparent; }
.panel-content::-webkit-scrollbar-thumb { background: rgba(0,180,255,0.2); border-radius: 2px; }
.timeline-track::-webkit-scrollbar { height: 4px; }
.timeline-track::-webkit-scrollbar-track { background: transparent; }
.timeline-track::-webkit-scrollbar-thumb { background: rgba(0,180,255,0.2); border-radius: 2px; }
</style>
