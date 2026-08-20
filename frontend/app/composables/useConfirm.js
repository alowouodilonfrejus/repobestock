import { reactive } from 'vue'

const state = reactive({
  visible: false,
  title: 'Confirmation',
  message: '',
  confirmLabel: 'Confirmer',
  danger: false,
  resolver: null,
})

export function useConfirm() {
  const confirmDialog = (options = {}) => {
    state.title = options.title || 'Confirmation'
    state.message = options.message || ''
    state.confirmLabel = options.confirmLabel || 'Confirmer'
    state.danger = options.danger ?? false
    state.visible = true
    return new Promise((resolve) => {
      state.resolver = resolve
    })
  }

  const closeConfirm = (result) => {
    state.visible = false
    if (state.resolver) state.resolver(result)
    state.resolver = null
  }

  return { state, confirmDialog, closeConfirm }
}