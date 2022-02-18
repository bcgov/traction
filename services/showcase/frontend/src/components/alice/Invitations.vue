<template>
  <div>
    <h2>Active Invitations</h2>
    {{ currentSandbox }}
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'Invitations',
  data() {
    return {
      loading: false,
    };
  },
  computed: {
    ...mapGetters('sandbox', ['sandboxes', 'currentSandbox']),
  },
};
</script>

<style>
</style>
