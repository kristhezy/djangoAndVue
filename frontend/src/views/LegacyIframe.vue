<template>
  <iframe :src="iframeSrc" style="width:100%;height:100%;border:none;"></iframe>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const iframeSrc = computed(() => {
  return `${route.path}?_plain=1`
})
</script>
