<template>
  <div>
    <v-card v-if="presentationRequests">
      <v-card-title> Pending Presentation Requests</v-card-title>
      <v-card
        v-for="pr in pendingPresentationRequests"
        :key="pr.id"
        class="ma-3"
      >
        <v-card-title class="grey lighten-3 mb-3">{{ pr.id }}</v-card-title>
        <v-card-text>
          <template v-for="(value, key) in pr">
            <div :key="key">
              <b>{{ key }}:</b> {{ value }}
            </div>
          </template>
          <!-- <v-expansion-panels>
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
          </v-expansion-panels> -->
        </v-card-text>
        <v-btn small color="primary" class="ma-4" @click="accept(pr.id)">
          Accept
        </v-btn>
        <v-btn small color="error" class="ma-4" @click="reject(pr.id)">
          Reject
        </v-btn>
      </v-card>
      <v-card-text>TBD</v-card-text>
    </v-card>
    <!--EMPTY-->
    <v-card v-else>
      <v-card-title> No Presentation Requests</v-card-title>
    </v-card>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'AlicePresentationRequests',
  data() {
    return {
      loading: false,
    };
  },
  computed: {
    ...mapGetters('alice', ['presentationRequests']),
    pendingPresentationRequests() {
      return this.presentationRequests;
    },
  },
  methods: {
    ...mapActions('alice', [
      'getPresentationRequests',
      'acceptPresentationRequests',
      'rejectPresentationRequests',
    ]),
    async accept(cred_offer_id) {
      await this.acceptPresentationRequests(cred_offer_id);
      await new Promise((r) => setTimeout(r, 1000)).then(() => {
        this.getPresentationRequests();
      });
    },
    async reject(cred_offer_id) {
      await this.rejectPresentationRequests(cred_offer_id);
      await new Promise((r) => setTimeout(r, 1000)).then(() => {
        this.getPresentationRequests();
      });
    },
  },
  async mounted() {
    await this.getPresentationRequests();
    this.loading = false;
  },
};
</script>

<style>
</style>
