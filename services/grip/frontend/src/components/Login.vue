<script setup lang="ts">
  let key = 'blah';
  const clicked = () => {
    console.log('clicked')
  }
</script>

<template>
  <div>{{key}}</div>
  <button @click="clicked">testing</button>
</template>

<style scoped>
</style>