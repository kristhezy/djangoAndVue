<template>
  <iframe :src="src" style="width:100%;height:100%;border:none;"></iframe>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const src = computed(() => route.query.goto ? `/${route.query.goto}` : '/home')
</script>
