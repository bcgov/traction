<template>
  <div>
    <h2>Current Sandbox sessions available</h2>
    <v-skeleton-loader :loading="loading" type="article">
      <p v-if="!sandboxes || !sandboxes.length">
        There are no Sandboxes currently available
      </p>
      {{ sandboxes }}
    </v-skeleton-loader>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'Sandboxes',
  data() {
    return {
      loading: true,
    };
  },
  computed: {
    ...mapGetters('sandbox', ['sandboxes']),
  },
  methods: {
    ...mapActions('sandbox', ['getSandboxes']),
  },
  async mounted() {
    await this.getSandboxes();
    this.loading = false;
  },
};
</script>

<style>
</style>
