<template>
  <v-container>
    <v-row class="mt-4">
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
  </v-container>
</template>

<script>
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
};
</script>
