<script setup lang="ts">
defineProps<{ open: boolean; title: string; width?: string }>()
defineEmits<{ close: [] }>()
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="modal-backdrop" @click.self="$emit('close')">
        <section class="modal-card" role="dialog" aria-modal="true" :aria-label="title" :style="{ maxWidth: width || '540px' }">
          <header><h2>{{ title }}</h2><button type="button" aria-label="Close" @click="$emit('close')">×</button></header>
          <div class="modal-body"><slot /></div>
          <footer v-if="$slots.footer"><slot name="footer" /></footer>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(4, 6, 9, 0.72);
  backdrop-filter: blur(14px) saturate(120%);
  display: grid;
  place-items: center;
  padding: 24px;
}
.modal-card {
  width: 100%;
  max-height: calc(100dvh - 48px);
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: #0d1116;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.6);
  overflow: hidden;
}
header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-subtle);
}
h2 {
  margin: 0;
  color: var(--text-strong);
  font-size: 13.5px;
  font-weight: 640;
  letter-spacing: -0.01em;
}
header button {
  width: 26px;
  height: 26px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: var(--text-faint);
  font-size: 17px;
  line-height: 1;
  cursor: pointer;
  transition: 0.14s;
}
header button:hover {
  background: rgba(255, 255, 255, 0.07);
  color: var(--text-strong);
}
.modal-body {
  min-height: 0;
  padding: 16px;
  overflow: auto;
}
.modal-card footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.015);
}
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.22s cubic-bezier(0.4, 0, 0.2, 1);
}
.modal-enter-active .modal-card {
  transition:
    transform 0.36s cubic-bezier(0.16, 1, 0.3, 1),
    opacity 0.24s cubic-bezier(0.4, 0, 0.2, 1);
}
.modal-leave-active .modal-card {
  transition:
    transform 0.18s cubic-bezier(0.4, 0, 1, 1),
    opacity 0.16s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .modal-card {
  transform: translateY(14px) scale(0.965);
  opacity: 0;
}
.modal-leave-to .modal-card {
  transform: translateY(6px) scale(0.99);
  opacity: 0;
}
@media (max-width: 720px) {
  .modal-backdrop { padding: 16px; }
  .modal-card { max-height: calc(100dvh - 32px); }
}
</style>
