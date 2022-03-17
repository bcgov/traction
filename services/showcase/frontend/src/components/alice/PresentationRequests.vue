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
          <template v-for="(value, key) in pr.presentation">
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
        <v-btn
          small
          color="primary"
          class="ma-4"
          @click="accept(pr.presentation.id)"
        >
          Accept
        </v-btn>
        <v-btn
          small
          color="error"
          class="ma-4"
          @click="reject(pr.presentation.id)"
        >
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
      return this.presentationRequests.filter(
        (pr) =>
          pr.presentation.present_state === 'request_received' &&
          pr.presentation.present_role === 'holder' &&
          (pr.workflow == undefined || pr.workflow.workflow_state !== 'error')
      );
    },
  },
  methods: {
    ...mapActions('alice', [
      'getPresentationRequests',
      'acceptPresentationRequest',
      'rejectPresentationRequest',
    ]),
    async accept(pres_req_id) {
      await this.acceptPresentationRequest(pres_req_id);
      await new Promise((r) => setTimeout(r, 1000)).then(() => {
        this.getPresentationRequests();
      });
    },
    async reject(pres_req_id) {
      await this.rejectPresentationRequest(pres_req_id);
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
