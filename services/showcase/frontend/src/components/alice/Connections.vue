<template>
  <v-card>
    <v-card-title> My Active Connections and Credentials</v-card-title>
    <v-card-text v-if="credentials && credentials.length">
      <v-card v-for="c in credentials" :key="c.id" class="ma-3">
        <v-card-title class="grey lighten-3 mb-3">{{
          currentSandbox.governance.schema_def.name
        }}</v-card-title>
        <v-card-text>
          <ul>
            <li><b>Degree: </b>{{ c.attrs.degree }}</li>
            <li><b>Completion Date: </b>{{ c.attrs.date }}</li>
            <li><b>Name: </b>{{ c.attrs.name }}</li>
            <li><b>Age: </b>{{ c.attrs.age }}</li>
            <li><b>Student ID: </b>{{ c.attrs.student_id }}</li>
            <hr class="my-2" />
            <li>
              <b>Issuer: </b>
              <a target="_blank" :href="nym_link(c.cred_def_id)">
                {{ issuer_name() }}
              </a>
            </li>
            <li>
              <b> Connection to Issuer: </b>
              Active
            </li>
          </ul>
          <v-expansion-panels class="mt-2">
            <v-expansion-panel>
              <v-expansion-panel-header> Details </v-expansion-panel-header>
              <v-expansion-panel-content>
                <div><b>cred_def_id:</b> {{ c.cred_def_id }}</div>
                <div><b>schema_id:</b> {{ c.schema_id }}</div>
                <div><b>date_received:</b> {{ c.attrs.date }}</div>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
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
    issuer_name() {
      return 'Faber University';
    },
    nym_link(cred_def_id) {
      return `http://test.bcovrin.vonx.io/browse/domain?page=1&query=${
        cred_def_id.split(':')[0]
      }&txn_type=1`;
    },
  },
  async mounted() {
    await this.getCredentials();
    this.loading = false;
  },
};
</script>

<style>
</style>
