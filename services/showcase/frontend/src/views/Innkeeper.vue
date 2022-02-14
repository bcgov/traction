<template>
  <v-container>
    <h1 class="my-6">Innkeeper</h1>
    <p>Set up and manage your current "Sandbox" session for the Showcase application</p>
    <Sandboxes />
    <SandboxCreate />
  </v-container>
</template>

<script>
import Sandboxes from '@/components/innkeeper/Sandboxes.vue';
import SandboxCreate from '@/components/innkeeper/SandboxCreate.vue';
export default {
  name: 'Innkeeper',
  components: {
    Sandboxes,
    SandboxCreate
  }
};
</script>
