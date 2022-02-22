<template>
  <v-card>
    <v-card-title>
      <v-icon large left color="primary"> mail </v-icon>
      <span class="text-h6">Messages</span>
    </v-card-title>

    <v-card-text>{{ ofbMessages }}</v-card-text>
  </v-card>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'AliceMessages',
  data() {
    return {
      loading: false,
    };
  },
  computed: {
    ...mapGetters('alice', ['ofbMessages']),
  },
  methods: {
    ...mapActions('alice', ['getOfbMessages']),
  },
  async mounted() {
    await this.getOfbMessages();
    this.loading = false;
  },
};
</script>

<style>
</style>
