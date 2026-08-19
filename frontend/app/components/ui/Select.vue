<template>
  <div class="mb-4">
    <label class="block text-sm text-gray-700 mb-1">{{ label }}</label>
    <select 
      :value="modelValue"
      class="w-full border border-gray-300 rounded p-2 text-sm"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <slot />
    </select>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  modelValue: [String, Number]
});
defineEmits(['update:modelValue']);
</script>
