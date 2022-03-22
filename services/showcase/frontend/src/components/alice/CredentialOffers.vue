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
            co.credential.cred_def_id
          }}</v-card-title>
          <v-card-text>
            <template
              v-for="(value, key) in JSON.parse(co.credential.credential)"
            >
              <div :key="key">
                <b>{{ key }}:</b> {{ value }}
              </div>
            </template>
            <v-expansion-panels>
              <v-expansion-panel>
                <v-expansion-panel-header> Details </v-expansion-panel-header>
                <v-expansion-panel-content>
                  <template v-for="(value, key) in co.credential">
                    <div :key="key">
                      <b>{{ key }}:</b> {{ value }}
                    </div>
                  </template>
                </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>
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
