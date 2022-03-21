<template>
  <v-card>
    <v-card-title> My Active Connections and Credentials</v-card-title>
    <v-card-text v-if="credentials && credentials.length">
      <v-card v-for="c in credentials" :key="c.id" class="ma-3">
        <v-card-title class="grey lighten-3 mb-3">{{
          currentSandbox.governance.schema_def.name
        }}</v-card-title>
        <v-card-text>
          <template v-for="(value, key) in c.attrs">
            <div :key="key">
              <b>{{ key }}:</b> {{ value }}
            </div>
          </template>
        </v-card-text>
      </v-card>
    </v-card-text>
    <v-card-text v-else>
      There are no active connections or credentials to show
    </v-card-text>
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
    ...mapGetters('sandbox', ['currentSandbox']),
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
