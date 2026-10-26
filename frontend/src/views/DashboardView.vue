<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import AppShell from '@/components/AppShell.vue'
import StatusPill from '@/components/StatusPill.vue'
import { messages } from '@/i18n/messages'
import { useCatalogStore } from '@/stores/catalog'
import { useCollectionStore } from '@/stores/collection'
import { useSessionStore } from '@/stores/session'

const router = useRouter()
const session = useSessionStore()
const catalog = useCatalogStore()
const collection = useCollectionStore()
const copy = computed(() => messages[session.locale])
const stats = computed(() => session.session.Statistics)
const preview = computed(() => collection.pals.slice(0, 6))
const actions = computed(() => [
  { icon: 'plus', title: copy.value.dashboard.addPal, copy: copy.value.dashboard.addPalHint, to: '/pals?add=1' },
  { icon: 'users', title: copy.value.dashboard.editPlayers, copy: copy.value.dashboard.editPlayersHint, to: '/players' },
  { icon: 'book', title: copy.value.dashboard.technology, copy: copy.value.dashboard.technologyHint, to: '/technology' },
  { icon: 'box', title: copy.value.dashboard.items, copy: copy.value.dashboard.itemsHint, to: '/items' },
  { icon: 'paw', title: copy.value.dashboard.browsePals, copy: copy.value.dashboard.browsePalsHint, to: '/pals' },
])

onMounted(async () => {
  await session.bootstrap()
  if (!session.loaded) {
    router.replace('/')
    return
  }
  await Promise.all([catalog.load(), collection.loadPals(), collection.loadPlayers()])
})
</script>

<template>
  <AppShell :eyebrow="copy.dashboard.eyebrow" :title="copy.dashboard.title">
    <section class="page-head">
      <p>{{ copy.dashboard.intro }}</p>
      <code>{{ session.session.Path }}</code>
    </section>

    <!-- 统计条 -->
    <section class="panel">
      <div class="metrics">
        <div class="metric"><div class="k">{{ copy.dashboard.players }}</div><div class="v"><b>{{ stats.Players }}</b></div></div>
        <div class="metric"><div class="k">{{ copy.dashboard.pals }}</div><div class="v"><b>{{ stats.Pals }}</b></div></div>
        <div class="metric"><div class="k">{{ copy.dashboard.humans }}</div><div class="v"><b>{{ stats.Humans }}</b></div></div>
        <div class="metric alert"><div class="k">{{ copy.dashboard.anomalies }}</div><div class="v"><b>{{ stats.Anomalies }}</b></div></div>
      </div>
    </section>

    <!-- 两栏 -->
    <div class="split">
      <section class="panel">
        <div class="panel-head">
          <h2>{{ copy.dashboard.actionsTitle }}</h2>
          <span>{{ actions.length }}</span>
        </div>
        <div class="ops">
          <RouterLink v-for="action in actions" :key="action.title" :to="action.to" class="op">
            <span class="ic"><AppIcon :name="action.icon" :size="15" /></span>
            <span class="t"><b>{{ action.title }}</b><span>{{ action.copy }}</span></span>
            <AppIcon name="chevron" :size="14" class="arrow" />
          </RouterLink>
        </div>
      </section>

      <div>
        <section class="panel">
          <div class="panel-head"><h2>{{ copy.dashboard.issueTitle }}</h2></div>
          <div class="panel-body">
            <div class="note">
              <AppIcon name="alert" :size="14" />
              <span>{{ copy.dashboard.issueCopy }}</span>
            </div>
            <RouterLink to="/pals?anomaly=yes" class="btn-full">{{ copy.dashboard.inspect }}</RouterLink>
          </div>
        </section>

        <section class="panel">
          <div class="panel-head"><h2>{{ copy.nav.loadedWorld }}</h2></div>
          <div class="panel-body kv-body">
            <div class="kv"><span class="k">{{ copy.nav.loadedWorld }}</span><span class="v">{{ session.worldName || copy.nav.noWorld }}</span></div>
            <div class="kv"><span class="k">{{ copy.pals.total }}</span><span class="v mono">{{ stats.Objects }}</span></div>
          </div>
        </section>
      </div>
    </div>

    <!-- 对象表格 -->
    <section class="panel">
      <div class="panel-head">
        <h2>{{ copy.dashboard.recent }}</h2>
        <span>{{ stats.Objects }} {{ copy.pals.total }}</span>
        <div class="acts"><RouterLink to="/pals" class="btn-sm">{{ copy.dashboard.viewAll }}</RouterLink></div>
      </div>
      <table v-if="preview.length" class="table">
        <thead>
          <tr><th>{{ copy.dashboard.recent }}</th><th>{{ copy.common.location }}</th><th>{{ copy.common.level }}</th><th>{{ copy.common.owner }}</th></tr>
        </thead>
        <tbody>
          <tr v-for="pal in preview" :key="pal.InstanceId">
            <td>
              <RouterLink :to="`/pals/${pal.InstanceId}`" class="obj">
                <img :src="`/image/pals/${pal.IconAccessKey}`" alt="" />
                <span class="obj-t">
                  <b>{{ pal.SpeciesName }}</b>
                  <span>{{ pal.NickName || pal.CharacterID }}</span>
                </span>
              </RouterLink>
            </td>
            <td><StatusPill :tone="pal.IsAnomalous ? 'gold' : 'neutral'">{{ copy.locations[pal.Location] }}</StatusPill></td>
            <td><span class="lv">Lv.{{ pal.Level }}</span></td>
            <td><span class="tag">{{ pal.OwnerName || copy.common.none }}</span></td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty">{{ collection.loading ? copy.common.loading : copy.common.noResults }}</p>
    </section>
  </AppShell>
</template>

<style scoped>
/* 页头 */
.page-head{margin-bottom:20px}
.page-head h1{margin:0 0 6px;color:var(--text-strong);font-size:22px;font-weight:700;letter-spacing:-.02em}
.page-head p{margin:0;color:var(--text-muted);font-size:12.5px;line-height:1.6}
.page-head code{display:block;max-width:900px;margin-top:5px;overflow:hidden;color:var(--text-faint);font-size:10.5px;white-space:nowrap;text-overflow:ellipsis}

/* 统一面板 */
.panel{border:1px solid var(--border-subtle);border-radius:var(--radius-lg);background:var(--surface);overflow:hidden}
.split{display:grid;grid-template-columns:1.55fr 1fr;gap:14px;align-items:start;margin-top:14px}
.split + .panel{margin-top:14px}
.panel-head{display:flex;align-items:center;gap:10px;padding:13px 16px;border-bottom:1px solid var(--border-subtle)}
.panel-head h2{margin:0;color:var(--text-strong);font-size:12.5px;font-weight:640}
.panel-head span{color:var(--text-faint);font-size:11px}
.panel-head .acts{margin-left:auto;display:flex;gap:6px}
.panel-body{padding:14px 16px}
.kv-body{padding-top:4px;padding-bottom:6px}

/* 统计条 */
.metrics{display:grid;grid-template-columns:repeat(4,1fr)}
.metric{padding:16px 18px;position:relative}
.metric + .metric{border-left:1px solid var(--border-subtle)}
.metric .k{color:var(--text-faint);font-size:10.5px}
.metric .v{display:flex;align-items:baseline;gap:5px;margin-top:6px}
.metric .v b{color:var(--text-strong);font-size:26px;font-weight:700;letter-spacing:-.03em;font-family:var(--mono);line-height:1}
.metric.alert .v b{color:#ffb26b}

/* 快捷操作 */
.ops{display:grid;grid-template-columns:1fr 1fr}
.op{display:flex;align-items:center;gap:11px;padding:12px 16px;border-bottom:1px solid var(--border-subtle);text-decoration:none;transition:.14s;min-width:0}
.op:nth-child(odd){border-right:1px solid var(--border-subtle)}
.op:hover{background:rgba(255,255,255,.035)}
.op .ic{width:30px;height:30px;flex:0 0 30px;display:grid;place-items:center;border-radius:9px;background:rgba(255,255,255,.06);color:var(--text-muted)}
.op .t{min-width:0;flex:1;display:flex;flex-direction:column}
.op .t b{color:var(--text-strong);font-size:12.5px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.op .t span{color:var(--text-faint);font-size:10.5px;margin-top:1px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.op .arrow{color:var(--text-faint);opacity:.5}
.op:hover .arrow{opacity:1;color:var(--cyan-300)}

/* 提示 */
.note{display:flex;gap:10px;padding:12px 13px;border-radius:11px;background:rgba(255,178,107,.07);border:1px solid rgba(255,178,107,.18);color:#ffca92;font-size:11px;line-height:1.6}
.note :deep(.app-icon){flex-shrink:0;margin-top:1px;color:#ffb26b}
.btn-full{display:flex;align-items:center;justify-content:center;height:30px;margin-top:12px;border:1px solid var(--border-subtle);border-radius:8px;color:var(--text-muted);font-size:11.5px;text-decoration:none;transition:.14s}
.btn-full:hover{background:rgba(255,255,255,.05);color:var(--text-strong)}

/* 表格 */
.table{width:100%;border-collapse:collapse}
.table th{padding:9px 16px;border-bottom:1px solid var(--border-subtle);text-align:left;color:var(--text-faint);font-size:10px;font-weight:650;letter-spacing:.06em;text-transform:uppercase}
.table td{padding:9px 16px;border-bottom:1px solid var(--border-subtle);font-size:12px;vertical-align:middle}
.table tr:last-child td{border-bottom:0}
.table tr:hover td{background:rgba(255,255,255,.025)}
.obj{display:flex;align-items:center;gap:10px;text-decoration:none}
.obj img{width:28px;height:28px;object-fit:contain;border-radius:8px;background:rgba(255,255,255,.04);flex-shrink:0}
.obj-t{display:flex;flex-direction:column;min-width:0}
.obj-t b{color:var(--text-strong);font-size:12.5px;font-weight:560;line-height:1.3}
.obj-t span{color:var(--text-faint);font-size:10.5px;line-height:1.3}
.lv{font-family:var(--mono);font-size:10px;padding:1px 5px;border-radius:4px;background:rgba(255,255,255,.07);color:var(--text-muted)}
.tag{font-size:10px;padding:1px 6px;border-radius:4px;background:rgba(255,255,255,.06);color:var(--text-faint)}
.btn-sm{display:inline-flex;align-items:center;height:26px;padding:0 10px;border:1px solid var(--border-subtle);border-radius:7px;color:var(--text-muted);font-size:11.5px;text-decoration:none;transition:.14s}
.btn-sm:hover{background:rgba(255,255,255,.05);color:var(--text-strong)}
.kv{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:1px solid var(--border-subtle);font-size:11.5px}
.kv:last-child{border-bottom:0}
.kv .k{color:var(--text-faint)}
.kv .v{color:var(--text-muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.kv .v.mono{font-family:var(--mono);font-size:11px}
.empty{padding:36px;color:var(--text-muted);font-size:12px;text-align:center}

@media(max-width:1280px){
  .split{grid-template-columns:1fr}
  .metrics{grid-template-columns:repeat(2,1fr)}
  .metric:nth-child(3){border-left:0}
  .metric:nth-child(n+3){border-top:1px solid var(--border-subtle)}
}
@media(max-width:900px){
  .ops{grid-template-columns:1fr}
  .op:nth-child(odd){border-right:0}
}
</style>
