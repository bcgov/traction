<script setup lang="ts">
import { inject } from "vue";

const store: any = inject("store");
</script>

<template>
  {{ store.state.token }}
</template>

<style></style>
