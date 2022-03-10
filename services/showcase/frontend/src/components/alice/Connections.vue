<template>
  <v-card>
    <v-card-title> My Active Connections and Credentials</v-card-title>
    <v-card v-for="c in credentials" :key="c.id" class="ma-3">
      <v-card-title class="grey lighten-3 mb-3">{{
        c.cred_def_id
      }}</v-card-title>
      <v-card-text>
        <template v-for="(value, key) in c.attrs">
          <div :key="key">
            <b>{{ key }}:</b> {{ value }}
          </div>
        </template>
      </v-card-text>
    </v-card>
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
