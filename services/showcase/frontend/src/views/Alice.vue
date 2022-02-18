<template>
  <v-container>
    <h1 class="my-6 text-center">Alice's Profile</h1>
    <Invitations />
  </v-container>
</template>

<script>
import Invitations from '@/components/alice/Invitations.vue';

export default {
  name: 'Alice',
  components: {
    Invitations
  }
};
</script>
