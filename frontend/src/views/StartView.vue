<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import BrandLockup from '@/components/BrandLockup.vue'
import LanguageToggle from '@/components/LanguageToggle.vue'
import ModalDialog from '@/components/ModalDialog.vue'
import StatusPill from '@/components/StatusPill.vue'
import { messages } from '@/i18n/messages'
import { ApiError, apiClient } from '@/services/apiClient'
import { useCatalogStore } from '@/stores/catalog'
import { useCollectionStore } from '@/stores/collection'
import { useSessionStore } from '@/stores/session'
import type { PathContext, SaveKind } from '@/types/domain'

const router = useRouter()
const session = useSessionStore()
const catalog = useCatalogStore()
const collection = useCollectionStore()
const copy = computed(() => messages[session.locale])
const selectedPath = ref('')
const browserOpen = ref(false)
const browser = ref<PathContext | null>(null)
const browserBusy = ref(false)
const directPath = ref('')
const saveKind = ref<SaveKind>('local')
type PathErrorKey = 'pathInvalid' | 'pathNotFound' | 'pathDenied' | 'pathUnavailable'
const browserErrorKey = ref<PathErrorKey | ''>('')
const featureIcons = ['paw', 'spark', 'dna', 'bolt', 'briefcase', 'book']
const candidatePath = computed(() => selectedPath.value || session.config?.Path || session.session.Path || '')
const browserError = computed(() => browserErrorKey.value ? copy.value.start[browserErrorKey.value] : '')

async function ensureReady() {
  if (!session.initialized) await session.bootstrap()
}

async function openBrowser() {
  await ensureReady()
  browserOpen.value = true
  return updateBrowser(() => apiClient.getPathContext())
}

async function browseTo(path: string) {
  await updateBrowser(() => apiClient.browsePath(path))
}

async function browseBack() {
  await updateBrowser(() => apiClient.pathBack())
}

async function browseDirect() {
  const path = directPath.value.trim()
  if (!path) {
    browserErrorKey.value = 'pathInvalid'
    return
  }
  await browseTo(path)
}

async function updateBrowser(action: () => Promise<PathContext>) {
  browserBusy.value = true
  browserErrorKey.value = ''
  try {
    const context = await action()
    browser.value = context
    directPath.value = context.currentPath
    return true
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.httpStatus === 400) browserErrorKey.value = 'pathInvalid'
      else if (error.httpStatus === 403) browserErrorKey.value = 'pathDenied'
      else if (error.httpStatus === 404) browserErrorKey.value = 'pathNotFound'
      else browserErrorKey.value = 'pathUnavailable'
    } else {
      browserErrorKey.value = 'pathUnavailable'
    }
    return false
  } finally {
    browserBusy.value = false
  }
}

function rootLabel(root: string) {
  return root.replace(/[\\/]+$/, '') || root
}

function isActiveRoot(root: string) {
  const current = browser.value?.currentPath
  if (!current) return false
  const normalizedCurrent = current.replaceAll('/', '\\').replace(/\\+$/, '').toLocaleLowerCase()
  const normalizedRoot = root.replaceAll('/', '\\').replace(/\\+$/, '').toLocaleLowerCase()
  if (!normalizedRoot) return current.startsWith(root)
  return normalizedCurrent === normalizedRoot || normalizedCurrent.startsWith(`${normalizedRoot}\\`)
}

function selectCurrentFolder() {
  if (!browser.value) return
  selectedPath.value = browser.value.currentPath
  browserOpen.value = false
}

async function detectSave() {
  saveKind.value = 'local'
  const opened = await openBrowser()
  if (opened && browser.value?.isPalDir) selectCurrentFolder()
}

async function openSave() {
  if (!candidatePath.value) {
    await openBrowser()
    return
  }
  await ensureReady()
  if (!await session.loadSave(candidatePath.value, saveKind.value)) return
  collection.clear()
  await Promise.all([catalog.load(), collection.loadPals(true), collection.loadPlayers(true)])
  router.push('/dashboard')
}

function worldName(path: string) {
  if (!path) return ''
  return path.split(/[\\/]/).filter(Boolean).at(-1) || path
}

onMounted(() => {
  const el = document.querySelector<HTMLElement>('.glass-card')
  if (!el) return
  el.addEventListener('pointermove', (e) => {
    const r = el.getBoundingClientRect()
    el.style.setProperty('--mx', `${((e.clientX - r.left) / r.width) * 100}%`)
    el.style.setProperty('--my', `${((e.clientY - r.top) / r.height) * 100}%`)
  })
})
</script>

<template>
  <div class="start-screen">
    <div class="bg-layer" aria-hidden="true">
      <span class="blob b1" /><span class="blob b2" /><span class="blob b3" /><span class="blob b4" />
      <img class="bg-pal" src="/mock/pals/WorldTreeDragon.png" alt="" />
      <span class="vignette" />
    </div>

    <header class="top-bar">
      <BrandLockup />
      <div class="bar-spacer" />
      <StatusPill tone="cyan">{{ copy.common.beta }}</StatusPill>
      <LanguageToggle />
    </header>

    <main class="stage">
      <section class="hero-copy">
        <div class="eyebrow-line"><span>{{ copy.start.eyebrow }}</span></div>
        <h1>{{ copy.start.title }}</h1>
        <p class="hero-intro">{{ copy.start.intro }}</p>

        <div class="hero-actions">
          <button class="act primary wide" type="button" @click="openBrowser">
            <AppIcon name="folder" :size="17" />
            {{ copy.start.choose }}
          </button>
          <button class="act" type="button" @click="detectSave">
            <AppIcon name="search" :size="17" />
            {{ copy.start.detect }}
          </button>
        </div>

        <div class="warning-note">
          <AppIcon name="alert" :size="15" />
          <div>
            <strong>{{ copy.start.gameExitTitle }}</strong>
            <span>{{ copy.start.gameExitCopy }}</span>
          </div>
        </div>
      </section>

      <section class="open-panel glass-card">
        <img class="panel-art" src="/mock/pals/WorldTreeDragon.png" alt="" />
        <span class="glow" />

        <div class="kind-seg" role="group" :aria-label="copy.start.saveKind" :data-mode="saveKind">
          <span class="thumb" />
          <button type="button" :class="{ on: saveKind === 'local' }" :aria-pressed="saveKind === 'local'" @click="saveKind = 'local'">
            {{ copy.start.localSave }}<small>{{ copy.start.localSaveHint }}</small>
          </button>
          <button type="button" :class="{ on: saveKind === 'dedicated' }" :aria-pressed="saveKind === 'dedicated'" @click="saveKind = 'dedicated'">
            {{ copy.start.dedicatedSave }}<small>{{ copy.start.dedicatedSaveHint }}</small>
          </button>
        </div>

        <div class="candidate-row">
          <b>{{ copy.start.candidate }}</b>
          <span>{{ candidatePath ? '1' : '0' }}</span>
          <span class="bar-spacer" />
          <span class="badge" :class="{ off: !candidatePath }">{{ candidatePath ? 'Palworld 1.0' : '—' }}</span>
        </div>

        <div class="save-card" :class="{ empty: !candidatePath }">
          <span class="save-icon"><AppIcon name="file" :size="23" /></span>
          <div class="save-info">
            <b>{{ candidatePath ? worldName(candidatePath) : copy.nav.noWorld }}</b>
            <span>{{ candidatePath ? copy.start.compatible : copy.start.notSave }}</span>
          </div>
        </div>

        <div class="path-row">
          <AppIcon name="folder" :size="13" />
          <code>{{ candidatePath || '—' }}</code>
          <span class="bar-spacer" />
          <button type="button" @click="openBrowser">{{ copy.start.browse }}</button>
        </div>

        <p v-if="session.error" class="load-error"><AppIcon name="alert" :size="15" />{{ session.error }}</p>

        <div class="panel-actions">
          <button class="act" type="button" @click="openBrowser">{{ copy.start.browse }}</button>
          <button class="act primary wide" type="button" :disabled="session.busy" @click="openSave">
            {{ session.busy ? copy.common.loading : copy.start.open }}
            <AppIcon name="arrow-right" :size="16" />
          </button>
        </div>
      </section>
    </main>

    <section class="caps">
      <span class="caps-lead">{{ copy.start.featuresTitle }}</span>
      <span v-for="(name, index) in copy.start.featureNames" :key="name" class="cap" :data-i="index">
        <i /><AppIcon :name="featureIcons[index]" :size="14" />{{ name }}
      </span>
    </section>

    <footer class="start-foot">
      <span>{{ copy.start.compatible }}</span>
      <span class="dot-sep" />
      <span>{{ copy.start.featuresTitle }}</span>
      <span class="bar-spacer" />
      <code>PlM · Oodle</code>
    </footer>

    <ModalDialog :open="browserOpen" :title="copy.start.browseTitle" width="760px" @close="browserOpen = false">
      <div class="browser-roots"><span>{{ copy.start.locations }}</span><div class="root-list"><button v-for="root in browser?.roots" :key="root" type="button" :class="{ active: isActiveRoot(root) }" :aria-pressed="isActiveRoot(root)" :disabled="browserBusy" @click="browseTo(root)">{{ rootLabel(root) }}</button></div></div>
      <form class="direct-path" @submit.prevent="browseDirect"><label><span>{{ copy.start.directPath }}</span><input v-model="directPath" type="text" :placeholder="copy.start.pathPlaceholder" :disabled="browserBusy" @keydown.enter.prevent="browseDirect" /></label><button class="button secondary" type="submit" :disabled="browserBusy || !directPath.trim()">{{ copy.start.go }}</button></form>
      <p v-if="browserError" class="browser-error"><AppIcon name="alert" :size="16" />{{ browserError }}</p>
      <div class="browser-path"><span>{{ copy.start.currentFolder }}</span><code>{{ browser?.currentPath || '—' }}</code></div>
      <div class="browser-tools"><button class="button secondary" type="button" :disabled="browserBusy" @click="browseBack"><AppIcon name="arrow-left" :size="15" />{{ copy.start.up }}</button><StatusPill :tone="browser?.isPalDir ? 'green' : 'neutral'">{{ browser?.isPalDir ? copy.start.compatible : copy.start.notSave }}</StatusPill></div>
      <div class="folder-list">
        <button v-for="(child, path) in browser?.children" v-show="child.isDir" :key="path" type="button" :disabled="browserBusy" @click="browseTo(path)"><AppIcon name="folder" :size="17" /><span>{{ child.filename }}</span><AppIcon name="chevron" :size="14" /></button>
        <p v-if="browser && !Object.values(browser.children).some((child) => child.isDir)">{{ copy.start.emptyFolder }}</p>
      </div>
      <template #footer><button class="button secondary" type="button" :disabled="browserBusy" @click="browserOpen = false">{{ copy.common.cancel }}</button><button class="button primary" type="button" :disabled="browserBusy || !browser?.isPalDir" @click="selectCurrentFolder">{{ copy.start.useFolder }}</button></template>
    </ModalDialog>
  </div>
</template>

<style scoped>
/* ================= 底层背景 ================= */
.start-screen{
  position:relative; min-height:100vh; overflow:hidden; isolation:isolate;
  color:#f6fafd;
  background:radial-gradient(120% 90% at 22% 8%, #12242e 0%, #0a0f16 42%, #04060a 100%);
  display:flex; flex-direction:column;
}
.bg-layer{position:fixed; inset:0; z-index:0; overflow:hidden; pointer-events:none}
.blob{position:absolute; border-radius:50%; filter:blur(110px); mix-blend-mode:screen; will-change:transform}
.b1{width:62vw;height:62vw;left:-18vw;top:-24vw;background:radial-gradient(circle,#23b98d,transparent 66%);opacity:.55;animation:drift1 26s ease-in-out infinite}
.b2{width:54vw;height:54vw;right:-16vw;top:-16vw;background:radial-gradient(circle,#3a7dff,transparent 64%);opacity:.44;animation:drift2 33s ease-in-out infinite}
.b3{width:56vw;height:56vw;left:20vw;bottom:-38vw;background:radial-gradient(circle,#8b5cf6,transparent 68%);opacity:.36;animation:drift3 41s ease-in-out infinite}
.b4{width:36vw;height:36vw;right:4vw;bottom:-18vw;background:radial-gradient(circle,#ff8fb0,transparent 70%);opacity:.22;animation:drift1 30s ease-in-out infinite reverse}
@keyframes drift1{0%,100%{transform:translate3d(0,0,0) scale(1)}50%{transform:translate3d(4vw,3vw,0) scale(1.08)}}
@keyframes drift2{0%,100%{transform:translate3d(0,0,0) scale(1.05)}50%{transform:translate3d(-5vw,4vw,0) scale(.94)}}
@keyframes drift3{0%,100%{transform:translate3d(0,0,0) scale(.97)}50%{transform:translate3d(3vw,-4vw,0) scale(1.1)}}
.bg-pal{
  position:absolute; left:-6vw; bottom:-10vw; width:62vw; height:62vw; object-fit:contain;
  opacity:.09; filter:blur(6px) saturate(1.1);
  -webkit-mask-image:radial-gradient(circle at 42% 46%, #000 26%, transparent 70%);
  mask-image:radial-gradient(circle at 42% 46%, #000 26%, transparent 70%);
}
.vignette{position:absolute;inset:0;background:radial-gradient(120% 90% at 50% 42%, transparent 42%, rgba(0,0,0,.55) 100%)}

/* ================= 玻璃 ================= */
.glass-card{
  position:relative; border-radius:40px; overflow:hidden; isolation:isolate;
  background:linear-gradient(158deg, rgba(255,255,255,.115), rgba(255,255,255,.045) 46%, rgba(255,255,255,.075));
  backdrop-filter:blur(40px) saturate(180%);
  -webkit-backdrop-filter:blur(40px) saturate(180%);
  box-shadow:0 40px 100px rgba(0,0,0,.62), inset 0 1px 0 rgba(255,255,255,.26), inset 0 -1px 0 rgba(255,255,255,.05);
}
.glass-card::before{
  content:""; position:absolute; inset:0; pointer-events:none; border-radius:inherit; z-index:2;
  background:linear-gradient(180deg, rgba(255,255,255,.19), rgba(255,255,255,0) 22%);
}
.glass-card::after{
  content:""; position:absolute; inset:0; pointer-events:none; border-radius:inherit; z-index:3; padding:1px;
  background:conic-gradient(from 160deg at 50% 0%,
    rgba(92,238,192,.55), rgba(98,204,255,.35) 22%, transparent 42%,
    transparent 62%, rgba(179,156,255,.42) 80%, rgba(255,156,194,.4) 100%);
  -webkit-mask:linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite:xor; mask-composite:exclude; opacity:.75;
}
.panel-art{
  position:absolute; right:-44px; top:-52px; width:300px; height:300px; object-fit:contain;
  opacity:.13; pointer-events:none; z-index:0;
  -webkit-mask-image:radial-gradient(circle at 58% 42%, #000 22%, transparent 68%);
  mask-image:radial-gradient(circle at 58% 42%, #000 22%, transparent 68%);
}
.glow{
  position:absolute; inset:0; pointer-events:none; border-radius:inherit; z-index:1;
  background:radial-gradient(520px circle at var(--mx,50%) var(--my,0%), rgba(255,255,255,.14), transparent 58%);
  opacity:0; transition:opacity .45s ease;
}
.glass-card:hover .glow{opacity:1}

/* ================= 顶栏 ================= */
.top-bar{
  position:relative; z-index:5; display:flex; align-items:center; gap:12px;
  padding:20px 46px 6px;
}
.bar-spacer{flex:1}

/* ================= 主体 ================= */
.stage{
  position:relative; z-index:4; flex:1;
  width:min(1220px,100%); margin:0 auto; padding:14px 46px 6px;
  display:grid; grid-template-columns:1fr 1.02fr; gap:44px; align-items:center;
}
.eyebrow-line{display:flex;align-items:center;gap:9px;margin-bottom:16px}
.eyebrow-line::before{content:"";width:26px;height:1px;background:linear-gradient(90deg,#5ceec0,transparent)}
.eyebrow-line span{font-size:10px;font-weight:700;letter-spacing:.26em;text-transform:uppercase;color:#5ceec0}
.hero-copy h1{
  margin:0 0 16px; font-size:44px; line-height:1.08; font-weight:760; letter-spacing:-.042em;
  background:linear-gradient(178deg,#ffffff 24%,#c6d6e2 68%,#8fa4b3);
  -webkit-background-clip:text; background-clip:text; color:transparent;
  white-space:pre-line;
}
.hero-intro{margin:0 0 22px; max-width:400px; color:#8593a5; font-size:13px; line-height:1.72}
.hero-actions{display:flex; gap:11px; margin-bottom:18px}

/* ================= 按钮 ================= */
.act{
  display:inline-flex; align-items:center; justify-content:center; gap:8px;
  height:47px; padding:0 20px; border:1px solid rgba(255,255,255,.11);
  border-radius:15px; background:rgba(255,255,255,.085); color:#f6fafd;
  font:inherit; font-size:13.5px; font-weight:620; cursor:pointer; white-space:nowrap;
  transition:transform .24s cubic-bezier(.22,.9,.3,1.2), background .24s, box-shadow .24s;
}
.act:hover{background:rgba(255,255,255,.15); transform:translateY(-1px)}
.act.primary{
  border-color:transparent; color:#03140f;
  background:linear-gradient(158deg,#7cf5cd,#5ceec0 46%,#2ec495);
  box-shadow:0 16px 40px rgba(92,238,192,.34), inset 0 1px 0 rgba(255,255,255,.6);
}
.act.primary:hover{filter:brightness(1.05); transform:translateY(-2px); box-shadow:0 22px 50px rgba(92,238,192,.42), inset 0 1px 0 rgba(255,255,255,.6)}
.act.wide{flex:1}
.act:disabled{opacity:.45; cursor:not-allowed; transform:none}

.warning-note{
  display:flex; align-items:flex-start; gap:10px; max-width:412px; padding:12px 14px;
  border:1px solid rgba(255,207,125,.26); border-radius:15px;
  background:linear-gradient(158deg, rgba(255,207,125,.15), rgba(255,207,125,.045));
  color:#ffcf7d; backdrop-filter:blur(18px);
}
.warning-note div{display:flex;flex-direction:column;gap:2px}
.warning-note strong{font-size:12px}
.warning-note span{color:#ffdfae; font-size:11px; line-height:1.6}

/* ================= 面板内容 ================= */
.open-panel{
  padding:24px; display:flex; flex-direction:column;
}
.open-panel > *:not(.panel-art):not(.glow){position:relative;z-index:4}

.kind-seg{
  position:relative; display:grid; grid-template-columns:1fr 1fr; gap:4px;
  padding:4px; margin-bottom:18px; border-radius:16px;
  background:rgba(0,0,0,.32); border:1px solid rgba(255,255,255,.08);
}
.thumb{
  position:absolute; top:4px; left:4px; width:calc(50% - 4px); height:calc(100% - 8px);
  border-radius:13px; background:linear-gradient(158deg, rgba(255,255,255,.26), rgba(255,255,255,.11));
  box-shadow:0 8px 22px rgba(0,0,0,.4), inset 0 1px 0 rgba(255,255,255,.5);
  transition:transform .34s cubic-bezier(.22,.9,.3,1.2);
}
.kind-seg[data-mode="dedicated"] .thumb{transform:translateX(100%)}
.kind-seg button{
  position:relative; z-index:2; height:42px; border:0; border-radius:13px; background:transparent;
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:1px;
  font:inherit; font-size:12.5px; font-weight:640; color:#8593a5; cursor:pointer; transition:color .25s;
}
.kind-seg button small{font-size:9px; font-weight:500; color:#8593a5; letter-spacing:.01em}
.kind-seg button.on{color:#f6fafd}

.candidate-row{display:flex; align-items:baseline; gap:9px; margin-bottom:12px}
.candidate-row b{font-size:11.5px;font-weight:650;color:#c2cdda}
.candidate-row > span:not(.bar-spacer){font-size:10.5px;color:#8593a5}
.badge{
  font-size:9.5px; font-weight:650; padding:3px 8px; border-radius:7px;
  background:rgba(92,238,192,.15); color:#5ceec0; border:1px solid rgba(92,238,192,.24);
}
.badge.off{background:rgba(255,255,255,.06); color:#8593a5; border-color:rgba(255,255,255,.08)}

.save-card{
  display:flex; align-items:center; gap:14px; padding:16px 17px; border-radius:26px; cursor:pointer;
  background:linear-gradient(158deg, rgba(92,238,192,.16), rgba(92,238,192,.04));
  border:1px solid rgba(92,238,192,.3);
  box-shadow:0 14px 38px rgba(35,185,141,.16), inset 0 1px 0 rgba(255,255,255,.26);
  transition:transform .28s cubic-bezier(.22,.9,.3,1.2), box-shadow .28s;
}
.save-card:hover{transform:translateY(-2px); box-shadow:0 22px 54px rgba(35,185,141,.24), inset 0 1px 0 rgba(255,255,255,.3)}
.save-card.empty{background:rgba(255,255,255,.05); border-color:rgba(255,255,255,.08); box-shadow:none}
.save-icon{
  width:50px; height:50px; flex:0 0 50px; border-radius:17px; display:grid; place-items:center;
  background:linear-gradient(150deg,#8dfad6,#5ceec0 45%,#12866a); color:#03140f;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.55), 0 10px 24px rgba(0,0,0,.32);
}
.empty .save-icon{background:rgba(255,255,255,.08); color:#8593a5; box-shadow:none}
.save-info{min-width:0}
.save-info b{display:block; font-family:ui-monospace,"Cascadia Mono",Consolas,monospace; font-size:14px; font-weight:670; color:#f6fafd; overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.save-info span{display:block; margin-top:4px; font-size:10.5px; color:#8593a5}

.path-row{
  display:flex; align-items:center; gap:9px; margin-top:14px; padding:9px 12px;
  border-radius:13px; background:rgba(0,0,0,.28); border:1px solid rgba(255,255,255,.07);
  color:#8593a5; font-size:10.5px;
}
.path-row code{font-family:ui-monospace,"Cascadia Mono",Consolas,monospace; font-size:10px; color:#c2cdda; overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.path-row button{border:0;background:transparent;color:#c2cdda;font:inherit;font-size:10.5px;padding:3px 8px;border-radius:7px;cursor:pointer;transition:.2s}
.path-row button:hover{background:rgba(255,255,255,.1)}

.load-error{display:flex;align-items:center;gap:8px;margin:12px 0 0;color:#ff9cc2;font-size:12px}

.panel-actions{display:flex; gap:11px; margin-top:17px}

/* ================= 能力标签 ================= */
.caps{
  position:relative; z-index:4; width:min(1220px,100%); margin:0 auto;
  padding:16px 46px 0; display:flex; align-items:center; gap:8px; flex-wrap:wrap;
}
.caps-lead{font-size:10px;font-weight:650;letter-spacing:.16em;text-transform:uppercase;color:#8593a5;margin-right:4px}
.cap{
  display:inline-flex; align-items:center; gap:7px; height:31px; padding:0 12px;
  border-radius:999px; font-size:11px; color:#c2cdda;
  background:rgba(255,255,255,.055); border:1px solid rgba(255,255,255,.075);
  backdrop-filter:blur(16px); transition:.22s;
}
.cap:hover{background:rgba(255,255,255,.11);border-color:rgba(255,255,255,.14);transform:translateY(-1px)}
.cap i{width:5px;height:5px;border-radius:50%;flex-shrink:0;background:#5ceec0}
.cap[data-i="1"] i{background:#62ccff}
.cap[data-i="2"] i{background:#b39cff}
.cap[data-i="3"] i{background:#ffcf7d}
.cap[data-i="4"] i{background:#ff9cc2}
.cap[data-i="5"] i{background:#9fe0ff}

/* ================= 底部 ================= */
.start-foot{
  position:relative; z-index:4; width:min(1220px,100%); margin:0 auto;
  padding:14px 46px 20px; display:flex; align-items:center; gap:10px;
  font-size:10px; color:#8593a5; opacity:.85;
}
.start-foot code{font-family:ui-monospace,"Cascadia Mono",Consolas,monospace;font-size:9.5px}
.dot-sep{width:3px;height:3px;border-radius:50%;background:#8593a5;opacity:.55}

/* ================= 模态框（沿用原结构，微调配色） ================= */
.browser-roots{margin-bottom:12px}
.browser-roots>span,.direct-path label>span{display:block;margin-bottom:6px;color:var(--text-faint);font-size:12px;font-weight:700}
.root-list{display:flex;flex-wrap:wrap;gap:7px}
.root-list button{min-width:58px;height:36px;padding:0 11px;border:1px solid rgba(255,255,255,.12);border-radius:8px;background:rgba(255,255,255,.06);color:#c2cdda;font:inherit;font-size:13px;font-weight:750;cursor:pointer}
.root-list button:hover{border-color:rgba(92,238,192,.45);color:#5ceec0}
.root-list button.active{border-color:rgba(179,156,255,.5);background:rgba(179,156,255,.14);color:#b39cff}
.root-list button:disabled{opacity:.45;cursor:not-allowed}
.direct-path{margin-bottom:12px;display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:end;gap:8px}
.direct-path input{width:100%;height:40px;padding:0 11px;border:1px solid rgba(255,255,255,.12);border-radius:9px;outline:0;background:rgba(0,0,0,.35);color:#f6fafd;font:inherit;font-size:14px}
.direct-path input:focus{border-color:rgba(92,238,192,.55);box-shadow:0 0 0 3px rgba(92,238,192,.12)}
.direct-path .button{height:40px}
.browser-error{margin:0 0 12px;padding:9px 11px;display:flex;align-items:center;gap:8px;border:1px solid rgba(255,156,194,.26);border-radius:9px;background:rgba(255,156,194,.09);color:#ff9cc2;font-size:13px;line-height:1.45}
.browser-tools{display:flex;align-items:center;justify-content:space-between;margin:14px 0}
.folder-list{height:280px;overflow:auto;border:1px solid rgba(255,255,255,.1);border-radius:12px;background:rgba(0,0,0,.3)}
.folder-list button{width:100%;height:46px;padding:0 14px;display:flex;align-items:center;gap:10px;border:0;border-bottom:1px solid rgba(255,255,255,.07);background:transparent;color:#f6fafd;font:inherit;font-size:14px;text-align:left;cursor:pointer}
.folder-list button:hover{background:rgba(92,238,192,.09);color:#5ceec0}
.folder-list button:disabled{opacity:.45;cursor:not-allowed}
.folder-list button span{flex:1}
.folder-list>p{margin:0;padding:24px;color:#8593a5;font-size:13px;text-align:center}

/* ================= 响应式 ================= */
@media (max-width:1280px){
  .top-bar,.caps,.start-foot{padding-left:32px;padding-right:32px}
  .stage{padding:14px 32px 6px;gap:34px}
  .hero-copy h1{font-size:38px}
}
@media (max-width:1040px){
  .stage{grid-template-columns:1fr;gap:26px}
  .start-screen{overflow:auto}
}
@media (max-height:820px){
  .hero-copy h1{font-size:36px}
  .open-panel{padding:20px}
  .caps{padding-top:12px}
}
</style>
