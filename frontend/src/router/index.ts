import { createRouter, createWebHistory } from 'vue-router'
import StartView from '@/views/StartView.vue'
import DashboardView from '@/views/DashboardView.vue'
import PalsView from '@/views/PalsView.vue'
import PalDetailView from '@/views/PalDetailView.vue'
import PlayersView from '@/views/PlayersView.vue'
import TechnologyView from '@/views/TechnologyView.vue'
import ItemsView from '@/views/ItemsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'start', component: StartView },
    { path: '/dashboard', name: 'dashboard', component: DashboardView },
    { path: '/pals', name: 'pals', component: PalsView },
    { path: '/pals/:id', name: 'pal-detail', component: PalDetailView },
    { path: '/players', name: 'players', component: PlayersView },
    { path: '/technology', name: 'technology', component: TechnologyView },
    { path: '/items', name: 'items', component: ItemsView },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

/**
 * 页面切换使用浏览器原生 View Transitions（WebView2 / Chromium 111+）。
 * 不支持时自动退化为普通跳转。
 */
type ViewTransitionDocument = Document & {
  startViewTransition?: (update: () => unknown) => { finished: Promise<void> }
}

const doc = typeof document !== 'undefined' ? (document as ViewTransitionDocument) : null

if (doc?.startViewTransition) {
  const wrap = <T extends (...args: never[]) => Promise<unknown>>(original: T): T => {
    return ((...args: never[]) => {
      // 先发起真实导航，保留其 Promise（错误仍会向上传播）
      const navigation = original(...args)
      try {
        // 浏览器会等 navigation 完成后再截图，过渡因此覆盖整个切换过程
        const transition = doc.startViewTransition!(() => navigation)
        // 过渡被跳过或中断不算错误，吞掉即可
        transition.finished.catch(() => undefined)
      } catch {
        // startViewTransition 不可用或被打断时直接忽略
      }
      return navigation
    }) as unknown as T
  }
  router.push = wrap(router.push.bind(router)) as typeof router.push
  router.replace = wrap(router.replace.bind(router)) as typeof router.replace
}

export default router
