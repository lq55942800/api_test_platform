<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// 根组件
</script>

<style>
#app {
  font-family: system-ui, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #08060d;
  background-color: #f9fafb;
  min-height: 100vh;
}

/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
}

/* Element Plus 样式覆盖 */
.el-button--primary {
  --el-button-bg-color: #aa3bff;
  --el-button-border-color: #aa3bff;
  --el-button-hover-bg-color: #9333ea;
  --el-button-hover-border-color: #9333ea;
  --el-button-active-bg-color: #7c3aed;
  --el-button-active-border-color: #7c3aed;
}

.el-link--primary {
  --el-link-text-color: #aa3bff;
  --el-link-hover-text-color: #9333ea;
}

.el-checkbox__input.is-checked .el-checkbox__inner {
  background-color: #aa3bff;
  border-color: #aa3bff;
}

.el-input__wrapper:focus-within {
  box-shadow: 0 0 0 1px #aa3bff inset;
}

.el-select .el-input.is-focus .el-input__wrapper {
  box-shadow: 0 0 0 1px #aa3bff inset;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
