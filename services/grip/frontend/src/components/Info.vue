<script setup lang="ts">
import { inject } from "vue";

const store: any = inject("store");
</script>

<template>Here isss our token {{ store.state.token }}</template>

<style></style>
