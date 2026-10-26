<script setup lang="ts">
import { computed } from 'vue'
import { messages } from '@/i18n/messages'
import { useSessionStore } from '@/stores/session'

withDefaults(defineProps<{ compact?: boolean }>(), { compact: false })
const brandLogoUrl = '/avatar.png'
const session = useSessionStore()
const copy = computed(() => messages[session.locale] ?? messages['zh-CN'])
</script>

<template>
  <div class="brand-lockup" :class="{ compact }">
    <img :src="brandLogoUrl" alt="" class="brand-mark" />
    <div class="brand-words">
      <strong>{{ copy.common.product }}</strong>
      <span>VERSION {{ copy.common.version }}</span>
    </div>
  </div>
</template>

<style scoped>
.brand-lockup{display:flex;align-items:center;gap:12px;color:var(--text-strong)}
.brand-mark{width:46px;height:46px;filter:drop-shadow(0 8px 16px rgba(92,238,192,.16))}
.brand-words{display:flex;flex-direction:column;line-height:1.05;letter-spacing:-.02em;min-width:0}
.brand-words strong{font-size:16px;font-weight:760;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.brand-words span{margin-top:4px;color:var(--text-muted);font-size:10px;font-weight:650;letter-spacing:.18em}
.compact .brand-mark{width:38px;height:38px}.compact .brand-words strong{font-size:14px}.compact .brand-words span{font-size:9px}
</style>
