<template>
  <div class="mb-4">
    <label class="block text-sm text-gray-700 mb-1">{{ label }}</label>
    <input 
      :type="type" 
      :placeholder="placeholder" 
      :value="modelValue"
      :disabled="disabled"
      class="w-full border border-gray-300 rounded p-2 text-sm disabled:bg-gray-100 disabled:text-gray-500"
      @input="$emit('update:modelValue', $event.target.value)"
    >
  </div>
</template>

<script setup>
defineProps({
  label: String,
  type: { type: String, default: 'text' },
  placeholder: String,
  disabled: Boolean,
  modelValue: [String, Number]
});
defineEmits(['update:modelValue']);
</script>
