<script setup lang="ts">
import { ref } from "vue";

const key = ref(0);

const clicked = () => {
  key.value++;
};
</script>

<template>
  <div>{{ key }}</div>
  <button @click="clicked">testing</button>
</template>

<style scoped></style>
