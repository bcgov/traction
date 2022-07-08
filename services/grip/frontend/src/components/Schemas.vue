<script setup lang="ts">
import { inject } from "vue";
import Fieldset from "primevue/fieldset";
const store: any = inject("store");
</script>

<template>
  <Fieldset :toggleable="true">
    <template #legend>Schemas</template>
    Here is some text
  </Fieldset>
</template>
