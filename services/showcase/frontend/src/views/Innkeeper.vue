<template>
  <v-container>
    <h1 class="my-6">
      <v-img
        src="@/assets/images/traction_logo_bcgov.svg"
        class="my-3"
        contain
        height="100"
      />
      Innkeeper
    </h1>
    <p>
      Set up and manage your current "Sandbox" session for the Showcase
      application
    </p>
    <Sandboxes />
  </v-container>
</template>

<script>
import Sandboxes from '@/components/innkeeper/Sandboxes.vue';
export default {
  name: 'Innkeeper',
  components: {
    Sandboxes,
  },
};
</script>
