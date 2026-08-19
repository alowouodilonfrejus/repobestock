<template>
  <div class="mb-4">
    <label class="block text-sm text-gray-700 mb-1">{{ label }}</label>
    <textarea
      :placeholder="placeholder"
      :value="modelValue"
      rows="3"
      class="w-full border border-gray-300 rounded p-2 text-sm"
      @input="$emit('update:modelValue', $event.target.value)"
    ></textarea>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  placeholder: String,
  modelValue: [String, Number]
});
defineEmits(['update:modelValue']);
</script>