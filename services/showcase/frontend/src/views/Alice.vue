<template>
  <div class="alice-profile">
    <v-container>
      <v-app-bar shaped>
        <v-icon x-large color="blue">badge</v-icon>
        <h1 class="ml-4">Personal Profile</h1>
        <v-spacer></v-spacer>

        <v-btn icon>
          <v-icon>mdi-magnify</v-icon>
        </v-btn>

        <v-btn icon>
          <v-icon>mdi-heart</v-icon>
        </v-btn>

        <v-btn icon>
          <v-icon>mdi-dots-vertical</v-icon>
        </v-btn>
      </v-app-bar>
      <v-row class="mt-4" v-if="currentSandbox">
        <v-col md="3">
          <User />
        </v-col>
        <v-col md="6">
          <Connections />
        </v-col>
        <v-col md="3">
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
import { mapGetters } from 'vuex';

import Connections from '@/components/alice/Connections.vue';
import Messages from '@/components/alice/Messages.vue';
import User from '@/components/alice/User.vue';

export default {
  name: 'Alice',
  components: {
    Connections,
    Messages,
    User,
  },
  computed: {
    ...mapGetters('sandbox', ['currentSandbox']),
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
