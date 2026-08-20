import { reactive } from 'vue'

const state = reactive({
  toasts: [],
})

let nextId = 1

const DURATION = {
  success: 4000,
  error: 6000,
  warning: 5000,
  info: 4000,
}

function push(type, message) {
  const id = nextId++
  state.toasts.push({ id, type, message })
  setTimeout(() => dismiss(id), DURATION[type] || 4000)
  return id
}

function dismiss(id) {
  const index = state.toasts.findIndex((t) => t.id === id)
  if (index !== -1) state.toasts.splice(index, 1)
}

export function useToast() {
  return {
    toasts: state.toasts,
    success: (message) => push('success', message),
    error: (message) => push('error', message),
    warning: (message) => push('warning', message),
    info: (message) => push('info', message),
    dismiss,
  }
}