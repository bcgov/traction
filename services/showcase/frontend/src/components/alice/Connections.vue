<template>
  <v-card>
    <v-card-title> My Active Connections and Credentials</v-card-title>

    <v-card-text>TBD</v-card-text>
  </v-card>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'AliceConnections',
  data() {
    return {
      loading: false,
    };
  },
  computed: {
    ...mapGetters('sandbox', ['sandboxes', 'currentSandbox']),
  },
};
</script>

<style>
</style>
