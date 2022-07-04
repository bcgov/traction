<script setup lang="ts">
import { inject } from "vue";
import Info from "./Info.vue";
import CreateContact from "./CreateContact.vue";

const store: any = inject("store");
</script>

<template>
  <div>
    <Info />
    <CreateContact />
  </div>
</template>


<script lang="ts">
export default {
  name: "TenantDashboard",
};
</script>

<style></style>
