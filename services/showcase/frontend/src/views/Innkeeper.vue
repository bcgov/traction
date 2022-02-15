<template>
  <v-container>
    <h1 class="my-6">Innkeeper</h1>
    <p>Set up and manage your current "Sandbox" session for the Showcase application</p>
    <Sandboxes />
  </v-container>
</template>

<script>
import Sandboxes from '@/components/innkeeper/Sandboxes.vue';
export default {
  name: 'Innkeeper',
  components: {
    Sandboxes
  }
};
</script>
