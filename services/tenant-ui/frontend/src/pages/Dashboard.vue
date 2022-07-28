<script setup lang="ts">
import Info from "../components/Info.vue";
import Contacts from "../components/Contacts.vue";
import Schemas from "../components/Schemas.vue";
</script>

<template>
  <Info class="information" />
  <Contacts class="information" />
  <Schemas class="information" />
</template>

<style scoped>
.information {
  margin: 1rem 0;
}
</style>
