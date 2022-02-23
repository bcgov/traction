<template>
  <v-container>
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
      <p class="mt-10">No sandbox session set, please go to Innkeeper tab to set that up</p>
    </v-row>
  </v-container>
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
