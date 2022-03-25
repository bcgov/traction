<template>
  <div v-if="presentationRequests && presentationRequests.length">
    <v-card class="pa-3">
      <v-card-title> Pending Presentation Requests</v-card-title>
      <v-card
        v-for="pr in pendingPresentationRequests"
        :key="pr.id"
        class="ma-3"
      >
        <!-- this is not accurate, you will not know what the credential request is for... only in this specific demo -->
        <v-card-title class="grey lighten-3 mb-3">{{
          currentSandbox.governance.schema_def.name
        }}</v-card-title>
        <v-card-text>
          <div><b>Verifier: </b> {{ connection_label(pr.connection_id) }}</div>
          <div
            v-for="key in ['connection_id', 'created_at', 'present_state']"
            :key="key"
          >
            <b>{{ key | keyToLabel }}: </b> {{ pr.presentation[key] }}
          </div>
          <hr />
          <b>Requested Data:</b>
          <ul>
            <div
              v-for="attr in JSON.parse(pr.presentation.present_request)
                .requested_attributes"
              :key="attr.name"
            >
              <li>
                <b>{{ attr.name | keyToLabel }} </b>
                <br /><i>RESTRICTIONS:</i> <br />
                <div class="ml-2">
                  <ul>
                    <li>
                      cred_def_id ==
                      {{ attr.restrictions[0].cred_def_id }}
                    </li>
                  </ul>
                </div>
              </li>
            </div>
          </ul>

          <v-expansion-panels>
            <v-expansion-panel>
              <v-expansion-panel-header> Details </v-expansion-panel-header>
              <v-expansion-panel-content>
                <div v-for="(value, key) in pr.presentation" :key="key">
                  <b>{{ key | keyToLabel }}: </b> {{ value }}
                </div>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-card-text>
        <v-btn
          small
          color="primary"
          class="white--text ma-4"
          @click="accept(pr.presentation.id)"
        >
          Accept
        </v-btn>
        <v-btn
          small
          color="error"
          class="white--text ma-4"
          @click="reject(pr.presentation.id)"
        >
          Reject
        </v-btn>
      </v-card>
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
    ...mapGetters('sandbox', ['currentSandbox']),
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
    connection_label() {
      // This needs to take connection_id and map it through the store
      return 'Acme';
    },
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
