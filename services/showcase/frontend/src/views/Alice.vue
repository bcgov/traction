<template>
  <div class="alice-profile">
    <v-container>
      <v-app-bar shaped>
        <v-icon x-large color="blue">badge</v-icon>
        <h2 class="ml-4">Personal Profile</h2>
        <v-spacer></v-spacer>

        <v-btn icon @click="refreshAlice">
          <v-icon>refresh</v-icon>
        </v-btn>

        <span class="d-none d-sm-flex">
          <v-btn icon>
            <v-icon>mdi-magnify</v-icon>
          </v-btn>

          <v-btn icon>
            <v-icon>mdi-heart</v-icon>
          </v-btn>

          <v-btn icon>
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </span>
      </v-app-bar>
      <v-row class="mt-4" v-if="currentSandbox">
        <v-col cols="12" sm="4" md="3">
          <User />
        </v-col>
        <v-col cols="12" sm="8" md="6">
          <CredentialOffers class="mb-4"/>
          <PresentationRequests class="mb-4"/>
          <Connections />
        </v-col>
        <v-col cols="12" sm="4" md="3">
          <Messages />
        </v-col>
      </v-row>
      <v-row v-else>
        <p class="mt-10">
          No sandbox session set, please go to Innkeeper tab to set that up
        </p>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';

import Connections from '@/components/alice/Connections.vue';
import CredentialOffers from '../components/alice/CredentialOffers.vue';
import Messages from '@/components/alice/Messages.vue';
import User from '@/components/alice/User.vue';
import PresentationRequests from '../components/alice/PresentationRequests.vue';

export default {
  name: 'Alice',
  components: {
    Connections,
    Messages,
    User,
    CredentialOffers,
    PresentationRequests,
  },
  data() {
    return {
      loading: false,
    };
  },
  computed: {
    ...mapGetters('sandbox', ['currentSandbox']),
  },
  methods: {
    ...mapActions('alice', ['refreshLob']),
    async refreshAlice() {
      this.loading = true;
      await this.refreshLob();
      this.loading = false;
    },
  },
};
</script>

<style lang="scss">
.alice-profile {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif !important;
  background-color: #dbdbdb !important;
}
</style>
