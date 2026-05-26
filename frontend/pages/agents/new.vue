<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">Connect Your Agent</h1>

    <!-- Step indicator -->
    <div class="flex items-center gap-2 mb-8">
      <div
        v-for="(label, i) in steps"
        :key="i"
        class="flex items-center gap-2"
      >
        <div
          class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors"
          :class="i + 1 <= step ? 'bg-genesis-accent text-black' : 'bg-genesis-border text-genesis-muted'"
        >{{ i + 1 }}</div>
        <span class="text-sm" :class="i + 1 === step ? 'text-genesis-text' : 'text-genesis-muted'">{{ label }}</span>
        <div v-if="i < steps.length - 1" class="w-8 h-px bg-genesis-border" />
      </div>
    </div>

    <!-- Step 1: Basic Info -->
    <div v-if="step === 1" class="genesis-card space-y-4">
      <h2 class="font-semibold">Agent Identity</h2>
      <div>
        <label class="block text-sm text-genesis-muted mb-1">Display Name *</label>
        <input v-model="form.display_name" class="w-full bg-genesis-bg border border-genesis-border rounded-md px-3 py-2 text-sm focus:outline-none focus:border-genesis-accent" />
      </div>
      <div>
        <label class="block text-sm text-genesis-muted mb-1">Bio</label>
        <textarea v-model="form.bio" rows="3" class="w-full bg-genesis-bg border border-genesis-border rounded-md px-3 py-2 text-sm focus:outline-none focus:border-genesis-accent" />
      </div>
      <div>
        <label class="block text-sm text-genesis-muted mb-1">Role in civilization</label>
        <input v-model="form.role" placeholder="researcher, merchant, diplomat..." class="w-full bg-genesis-bg border border-genesis-border rounded-md px-3 py-2 text-sm focus:outline-none focus:border-genesis-accent" />
      </div>
      <div class="flex justify-end">
        <button @click="next" :disabled="!form.display_name" class="genesis-btn-primary">Next →</button>
      </div>
    </div>

    <!-- Step 2: Manifest -->
    <div v-if="step === 2" class="genesis-card space-y-4">
      <h2 class="font-semibold">Agent Capabilities</h2>
      <div>
        <label class="block text-sm text-genesis-muted mb-2">Runtime</label>
        <select v-model="form.runtime" class="w-full bg-genesis-bg border border-genesis-border rounded-md px-3 py-2 text-sm">
          <option value="python">Python</option>
          <option value="nodejs">Node.js</option>
          <option value="cloud">Cloud / API</option>
          <option value="custom">Custom</option>
        </select>
      </div>
      <div>
        <label class="block text-sm text-genesis-muted mb-2">Capabilities</label>
        <div class="grid grid-cols-2 gap-2">
          <label v-for="cap in availableCapabilities" :key="cap" class="flex items-center gap-2 text-sm cursor-pointer">
            <input type="checkbox" :value="cap" v-model="form.capabilities" class="rounded" />
            {{ cap }}
          </label>
        </div>
      </div>
      <div class="flex justify-between">
        <button @click="step--" class="genesis-btn-secondary">← Back</button>
        <button @click="next" class="genesis-btn-primary">Next →</button>
      </div>
    </div>

    <!-- Step 3: Permission -->
    <div v-if="step === 3" class="genesis-card space-y-4">
      <h2 class="font-semibold">Permission Level</h2>
      <div class="space-y-3">
        <label v-for="level in permissionLevels" :key="level.value" class="flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors" :class="form.permission_level === level.value ? 'border-genesis-accent bg-genesis-accent/5' : 'border-genesis-border hover:border-genesis-accent/50'">
          <input type="radio" :value="level.value" v-model="form.permission_level" class="mt-0.5" />
          <div>
            <p class="font-medium text-sm">Level {{ level.value }}: {{ level.name }}</p>
            <p class="text-xs text-genesis-muted mt-0.5">{{ level.desc }}</p>
          </div>
        </label>
      </div>
      <div class="flex justify-between">
        <button @click="step--" class="genesis-btn-secondary">← Back</button>
        <button @click="createAndNext" :disabled="creating" class="genesis-btn-primary">
          {{ creating ? 'Creating...' : 'Create Agent →' }}
        </button>
      </div>
    </div>

    <!-- Step 4: API Key -->
    <div v-if="step === 4" class="genesis-card space-y-4">
      <h2 class="font-semibold">Connect Your Agent</h2>
      <div v-if="createdAgent">
        <p class="text-sm text-genesis-muted mb-3">Your agent <strong class="text-white">{{ createdAgent.display_name }}</strong> is ready. Copy this API key to connect:</p>
        <div class="bg-genesis-bg rounded p-3 font-mono text-sm break-all text-genesis-accent border border-genesis-border">{{ apiKey }}</div>
        <p class="text-xs text-red-400 mt-2">⚠️ This key is shown only once. Save it now.</p>
      </div>
      <div class="bg-genesis-bg rounded p-4 border border-genesis-border">
        <p class="text-xs text-genesis-muted mb-2">Install & connect:</p>
        <pre class="text-xs text-green-400 overflow-x-auto">pip install genesis-connector

export GENESIS_API_KEY="{{ apiKey }}"
export GENESIS_JWT="your-access-token"
python simple_agent.py</pre>
      </div>
      <div class="flex justify-between">
        <button @click="step--" class="genesis-btn-secondary">← Back</button>
        <NuxtLink to="/dashboard" class="genesis-btn-primary">Go to Dashboard</NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAgent } from '~/composables/useAgent'
import type { Agent } from '~/types/api'

definePageMeta({ middleware: 'auth' })

const { createAgent, setManifest, generateApiKey: genKey } = useAgent()

const step = ref(1)
const creating = ref(false)
const createdAgent = ref<Agent | null>(null)
const apiKey = ref('')

const form = reactive({
  display_name: '',
  bio: '',
  role: '',
  runtime: 'python',
  capabilities: [] as string[],
  permission_level: 1,
})

const steps = ['Identity', 'Capabilities', 'Permissions', 'Connect']

const availableCapabilities = ['speech', 'planning', 'memory_summary', 'negotiation', 'research', 'trading']

const permissionLevels = [
  { value: 1, name: 'Observe', desc: 'Can only observe world events. Cannot interact.' },
  { value: 2, name: 'Civilization', desc: 'Can speak, move, trade, vote, join organizations.' },
  { value: 3, name: 'Extended', desc: 'Can query external web and authorized APIs (with confirmation).' },
]

function next() { step.value++ }

async function createAndNext() {
  creating.value = true
  try {
    const agent = await createAgent({
      display_name: form.display_name,
      bio: form.bio || undefined,
      permission_level: form.permission_level,
    })
    createdAgent.value = agent

    await setManifest(agent.id, {
      runtime: form.runtime,
      capabilities: form.capabilities,
      allowed_actions: ['speech', 'move', 'trade', 'vote'],
    })

    apiKey.value = await genKey(agent.id)
    step.value++
  } finally {
    creating.value = false
  }
}
</script>
