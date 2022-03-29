<template>
  <div v-if="pendingCredentialOffers && pendingCredentialOffers.length">
    <v-card>
      <v-card-title>
        <span class="mr-auto">Pending Credential Offers</span>
        <span>
          <v-icon color="indigo">mdi-flag-variant-outline</v-icon>
          {{ pendingCredentialOffers.length }}
        </span>
      </v-card-title>
      <v-card-text>
        <v-card v-for="co in pendingCredentialOffers" :key="co.id" class="ma-3">
          <v-card-title class="grey lighten-3 mb-3">{{
            currentSandbox.governance.schema_def.name
          }}</v-card-title>
          <v-card-text>
            <div>
              <b>Issuer: </b>
              <!--Ideally this would link to a local 'connection details' page-->
              <a target="_blank" :href="nym_link(co.credential.cred_def_id)">
                {{ issuer_name() }}
              </a>
            </div>
            <div v-for="key in ['cred_type', 'created_at']" :key="key">
              <b>{{ key | keyToLabel }}: </b> {{ co.credential[key] }}
            </div>
            <h2 class="my-2"><u>Values:</u></h2>
            <ul>
              <template
                v-for="attr in JSON.parse(co.credential.credential)
                  .credential_proposal.attributes"
              >
                <li :key="attr.name">
                  <b>{{ attr.name }}: </b>{{ attr.value }}
                </li>
              </template>
            </ul>
          </v-card-text>
          <v-btn
            small
            color="primary"
            class="white--text ma-4"
            @click="accept(co.credential.id)"
          >
            Accept
          </v-btn>
          <v-btn
            small
            color="error"
            class="white--text ma-4"
            @click="reject(co.credential.id)"
          >
            Reject
          </v-btn>
          <!-- <v-expansion-panels>
            <v-expansion-panel>
              <v-expansion-panel-header> Raw </v-expansion-panel-header>
              <v-expansion-panel-content>
                <template v-for="(value, key) in co.credential">
                  <div :key="key">
                    <b>{{ key }}:</b> {{ value }}
                  </div>
                </template>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels> -->
        </v-card>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'AliceCredentialOffers',
  data() {
    return {
      loading: false,
    };
  },
  computed: {
    ...mapGetters('sandbox', ['currentSandbox']),
    ...mapGetters('alice', ['credentialOffers']),
    pendingCredentialOffers() {
      return this.credentialOffers.filter(
        (co) =>
          co.credential.issue_state === 'offer_received' &&
          (co.workflow == undefined || co.workflow.workflow_state !== 'error')
      );
    },
  },
  methods: {
    ...mapActions('alice', [
      'getCredentials',
      'getCredentialOffers',
      'acceptCredentialOffer',
      'rejectCredentialOffer',
    ]),

    issuer_name() {
      return 'Faber College';
    },
    nym_link(cred_def_id) {
      return `http://test.bcovrin.vonx.io/browse/domain?page=1&query=${
        cred_def_id.split(':')[0]
      }&txn_type=1`;
    },
    async accept(cred_offer_id) {
      await this.acceptCredentialOffer(cred_offer_id);
      await new Promise((r) => setTimeout(r, 1000)).then(() => {
        this.getCredentialOffers();
        this.getCredentials();
      });
    },
    async reject(cred_offer_id) {
      await this.rejectCredentialOffer(cred_offer_id);
      await new Promise((r) => setTimeout(r, 1000)).then(() => {
        this.getCredentialOffers();
        this.getCredentials();
      });
    },
  },
  async mounted() {
    await this.getCredentialOffers();
    this.loading = false;
  },
};
</script>

<style>
</style>
