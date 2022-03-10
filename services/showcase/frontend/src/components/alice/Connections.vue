<template>
  <v-card>
    <v-card-title> My Active Connections and Credentials</v-card-title>
    {{ credentials }}
    <v-card-text>TBD</v-card-text>
  </v-card>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'AliceConnections',
  data() {
    return {
      loading: false,
      credentials: [],
    };
  },
  computed: {
    ...mapGetters('alice', ['credentials']),
  },
  methods: {
    ...mapActions('alice', ['getCredentials']),
  },
  async mounted() {
    await this.getCredentials();
    this.loading = false;
  },
};
</script>

<style>
</style>
