<template>
  <el-tag
    :style="tagStyle"
    size="small"
    :effect="effect"
    round
  >
    {{ method }}
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { METHOD_COLORS } from '@/types/api'

const props = withDefaults(defineProps<{
  method: string
  effect?: 'dark' | 'light' | 'plain'
}>(), {
  effect: 'light'
})

const tagStyle = computed(() => {
  const colors = METHOD_COLORS[props.method?.toUpperCase()] || METHOD_COLORS.GET
  return {
    backgroundColor: colors.bg,
    color: colors.text,
    borderColor: colors.bg,
    fontWeight: 600,
    fontFamily: 'ui-monospace, Consolas, monospace',
    fontSize: '12px',
    minWidth: '56px',
    textAlign: 'center' as const
  }
})
</script>
