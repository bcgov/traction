<template>
  <v-row>
    <v-col cols="12" sm="6">
      <div v-if="tenant.cred_def_id">
        <v-icon color="success">check_circle_outline</v-icon> Faber College
        is an Issuer
      </div>
      <div v-else>
        <v-icon color="error">error_outline</v-icon> Faber College has not
        met the criteria to be an Issuer yet

        <v-tooltip bottom>
          <template #activator="{ on, attrs }">
            <v-btn
              large
              icon
              v-bind="attrs"
              v-on="on"
              @click="makeIssuer(tenant.id)"
            >
              <v-icon>forward_to_inbox</v-icon>
            </v-btn>
          </template>
          <span>Request Issuer status</span>
        </v-tooltip>
      </div>
    </v-col>
    <v-col cols="12" sm="6" class="text-sm-right">
      <v-btn class="mr-4" icon @click="$emit('refresh')">
        <v-icon>refresh</v-icon>
      </v-btn>
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <span v-bind="attrs" v-on="on">
            <v-icon>group</v-icon> office-admin-001
          </span>
        </template>
        <span>Not really logged in anywhere, just for show</span>
      </v-tooltip>
    </v-col>
  </v-row>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'FaberHeader',
  computed: {
    ...mapGetters('faber', ['tenant']),
  },
  methods: {
    ...mapActions('sandbox', ['makeIssuer']),
  },
};
</script>

<style>
</style>
