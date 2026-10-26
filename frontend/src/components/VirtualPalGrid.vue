<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import StatusPill from './StatusPill.vue'
import { messages } from '@/i18n/messages'
import { useSessionStore } from '@/stores/session'
import type { PalSummary } from '@/types/domain'
import { computeVirtualWindow } from '@/utils/virtualGrid'

const props = withDefaults(
  defineProps<{ items: PalSummary[]; variant?: 'grid' | 'list'; rowHeight?: number; overscan?: number }>(),
  { variant: 'grid', overscan: 4 },
)

const session = useSessionStore()
const copy = computed(() => messages[session.locale])
const viewport = ref<HTMLElement | null>(null)
const viewportWidth = ref(900)
const viewportHeight = ref(600)
const scrollTop = ref(0)
let observer: ResizeObserver | null = null

const isList = computed(() => props.variant === 'list')
const gap = computed(() => (isList.value ? 0 : 10))
const rowH = computed(() => props.rowHeight ?? (isList.value ? 49 : 218))
const columns = computed(() =>
  isList.value ? 1 : Math.max(1, Math.floor((viewportWidth.value + gap.value) / (248 + gap.value))),
)
const windowState = computed(() =>
  computeVirtualWindow(
    props.items.length,
    columns.value,
    rowH.value,
    viewportHeight.value,
    scrollTop.value,
    props.overscan,
  ),
)
const visibleItems = computed(() => props.items.slice(windowState.value.startIndex, windowState.value.endIndex))

function onScroll(event: Event) {
  scrollTop.value = (event.currentTarget as HTMLElement).scrollTop
}

function stateLabel(flag: string) {
  if (flag === 'outside-container') return copy.value.states.outside
  return copy.value.states[flag as keyof typeof copy.value.states] || flag
}

onMounted(() => {
  if (!viewport.value) return
  const update = () => {
    if (!viewport.value) return
    viewportWidth.value = viewport.value.clientWidth
    viewportHeight.value = viewport.value.clientHeight
  }
  update()
  if (typeof ResizeObserver !== 'undefined') {
    observer = new ResizeObserver(update)
    observer.observe(viewport.value)
  }
})
onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <div
    ref="viewport"
    class="virtual-viewport"
    :class="variant"
    data-testid="virtual-pal-grid"
    @scroll="onScroll"
  >
    <div :style="{ height: `${windowState.paddingTop}px` }" />

    <!-- 列表模式 -->
    <div v-if="isList" class="pal-rows">
      <RouterLink
        v-for="pal in visibleItems"
        :key="pal.InstanceId"
        :to="`/pals/${pal.InstanceId}`"
        class="pal-row"
        :data-instance-id="pal.InstanceId"
      >
        <img class="thumb" :src="`/image/pals/${pal.IconAccessKey}`" alt="" />
        <div class="cell name">
          <b>{{ pal.SpeciesName }}</b>
          <span>{{ pal.NickName || pal.CharacterID }}</span>
        </div>
        <div class="cell monospace">Lv.{{ pal.Level }}</div>
        <div class="cell">{{ copy.locations[pal.Location] }}</div>
        <div class="cell muted">{{ pal.OwnerName || copy.common.none }}</div>
        <div class="cell flags">
          <StatusPill :tone="pal.ObjectType === 'human' ? 'gold' : 'cyan'">
            {{ pal.ObjectType === 'human' ? copy.pals.typeHuman : copy.pals.typePal }}
          </StatusPill>
          <StatusPill v-for="flag in pal.StateFlags.slice(0, 2)" :key="flag" :tone="pal.IsAnomalous ? 'red' : 'gold'">
            {{ stateLabel(flag) }}
          </StatusPill>
        </div>
      </RouterLink>
    </div>

    <!-- 网格模式 -->
    <div v-else class="pal-grid" :style="{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }">
      <RouterLink
        v-for="pal in visibleItems"
        :key="pal.InstanceId"
        :to="`/pals/${pal.InstanceId}`"
        class="pal-card"
        :style="{ height: `${rowH - gap}px` }"
        :data-instance-id="pal.InstanceId"
      >
        <div class="portrait">
          <img :src="`/image/pals/${pal.IconAccessKey}`" alt="" />
          <span v-if="pal.PalDeckId">#{{ pal.PalDeckId }}</span>
        </div>
        <div class="pal-card-body">
          <h3>{{ pal.SpeciesName }}</h3>
          <p>{{ pal.NickName || pal.CharacterID }}</p>
          <dl>
            <div><dt>{{ copy.common.level }}</dt><dd>{{ pal.Level }}</dd></div>
            <div><dt>{{ copy.common.owner }}</dt><dd>{{ pal.OwnerName || copy.common.none }}</dd></div>
            <div><dt>{{ copy.common.location }}</dt><dd>{{ copy.locations[pal.Location] }}</dd></div>
          </dl>
        </div>
        <div class="card-flags">
          <StatusPill :tone="pal.ObjectType === 'human' ? 'gold' : 'cyan'">
            {{ pal.ObjectType === 'human' ? copy.pals.typeHuman : copy.pals.typePal }}
          </StatusPill>
          <StatusPill v-for="flag in pal.StateFlags.slice(0, 2)" :key="flag" :tone="pal.IsAnomalous ? 'red' : 'gold'">
            {{ stateLabel(flag) }}
          </StatusPill>
        </div>
      </RouterLink>
    </div>

    <div :style="{ height: `${windowState.paddingBottom}px` }" />
    <p v-if="!items.length" class="empty">{{ copy.common.noResults }}</p>
  </div>
</template>

<style scoped>
.virtual-viewport {
  height: calc(100vh - 268px);
  min-height: 420px;
  overflow: auto;
  padding-right: 4px;
}
.virtual-viewport.list { height: calc(100vh - 268px); }

/* ================= 列表模式 ================= */
.pal-rows {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: var(--surface);
  overflow: hidden;
}
.pal-row {
  display: grid;
  grid-template-columns: 32px minmax(140px, 1.4fr) 64px 90px 120px minmax(120px, 1fr);
  align-items: center;
  gap: 12px;
  height: 49px;
  padding: 0 14px;
  border-bottom: 1px solid var(--border-subtle);
  text-decoration: none;
  transition: background 0.13s;
}
.pal-row:last-child { border-bottom: 0; }
.pal-row:hover { background: rgba(255, 255, 255, 0.035); }
.thumb {
  width: 30px;
  height: 30px;
  object-fit: contain;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.04);
}
.cell { min-width: 0; font-size: 12px; color: var(--text); }
.cell.name { display: flex; flex-direction: column; line-height: 1.3; }
.cell.name b {
  font-size: 12.5px;
  font-weight: 560;
  color: var(--text-strong);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.cell.name span {
  font-size: 10.5px;
  color: var(--text-faint);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.cell.monospace { font-family: var(--mono); font-size: 11px; color: var(--text-muted); }
.cell.muted { color: var(--text-faint); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cell.flags { display: flex; gap: 5px; overflow: hidden; }

/* ================= 网格模式 ================= */
.pal-grid { display: grid; gap: 10px; }
.pal-card {
  position: relative;
  min-width: 0;
  padding: 14px;
  display: grid;
  grid-template-columns: 82px minmax(0, 1fr);
  grid-template-rows: 1fr auto;
  gap: 11px 13px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  background: var(--surface);
  text-decoration: none;
  overflow: hidden;
}
.pal-card:hover { background: rgba(255, 255, 255, 0.05); }
.portrait {
  position: relative;
  width: 82px;
  height: 82px;
  display: grid;
  place-items: center;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.04);
}
.portrait img { width: 76px; height: 76px; object-fit: contain; }
.portrait span {
  position: absolute;
  left: 5px;
  bottom: 4px;
  padding: 2px 5px;
  border-radius: 5px;
  background: rgba(5, 9, 17, 0.88);
  color: var(--cyan-300);
  font-size: 11px;
  font-weight: 800;
}
.pal-card-body { min-width: 0; }
.pal-card-body h3 {
  margin: 2px 0 3px;
  overflow: hidden;
  color: var(--text-strong);
  font-size: 14px;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.pal-card-body p {
  margin: 0;
  overflow: hidden;
  color: var(--text-muted);
  font-size: 12px;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.pal-card-body dl { margin: 9px 0 0; display: grid; gap: 4px; }
.pal-card-body dl div { min-width: 0; display: grid; grid-template-columns: 58px 1fr; gap: 5px; }
.pal-card-body dt { color: var(--text-faint); font-size: 11px; }
.pal-card-body dd {
  margin: 0;
  overflow: hidden;
  color: var(--text);
  font-size: 11px;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.card-flags { grid-column: 1/-1; display: flex; align-items: center; gap: 5px; overflow: hidden; }
.empty { padding: 40px; color: var(--text-muted); font-size: 12px; text-align: center; }

@media (max-width: 1180px) {
  .pal-row { grid-template-columns: 32px minmax(120px, 1.4fr) 60px 80px minmax(100px, 1fr); }
  .cell.flags { display: none; }
}
</style>
