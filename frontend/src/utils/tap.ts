/**
 * 点击反馈：从鼠标位置扩散一圈波纹。
 *
 * 只使用一次性 animation（挂在临时创建的 span 上），
 * 元素本身不重播动画，所以不会闪。
 */

const RIPPLE_SELECTOR = [
  'button',
  '.button',
  '.act',
  '.op',
  '.pal-card',
  '.pal-row',
  '.nav-item',
  '.cap',
  '.btn-sm',
  '.btn-full',
  '.toggle',
  '.pal-search input',
  '.setting-row',
].join(',')

function createRipple(element: HTMLElement, clientX: number, clientY: number) {
  const rect = element.getBoundingClientRect()
  if (!rect.width || !rect.height) return

  const size = Math.max(rect.width, rect.height) * 1.7
  const ripple = document.createElement('span')
  ripple.className = 'tap-ripple'
  ripple.style.width = `${size}px`
  ripple.style.height = `${size}px`
  ripple.style.left = `${clientX - rect.left - size / 2}px`
  ripple.style.top = `${clientY - rect.top - size / 2}px`

  element.appendChild(ripple)
  ripple.addEventListener('animationend', () => ripple.remove(), { once: true })
  window.setTimeout(() => ripple.remove(), 900)
}

if (typeof document !== 'undefined') {
  document.addEventListener(
    'pointerdown',
    (event) => {
      if (event.button !== 0) return
      const target = event.target as HTMLElement | null
      const element = target?.closest<HTMLElement>(RIPPLE_SELECTOR)
      if (!element) return
      if (element.hasAttribute('disabled') || element.getAttribute('aria-disabled') === 'true') return

      if (getComputedStyle(element).position === 'static') {
        element.style.position = 'relative'
      }
      createRipple(element, event.clientX, event.clientY)
    },
    { passive: true },
  )
}

export {}
