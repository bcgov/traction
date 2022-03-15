<template>
  <v-card
    class="mx-auto"
    outlined
    tile
    @click="SET_SELECTED_APPLICANT(applicant)"
  >
    <v-system-bar color="rgba(0, 160, 144)" />
    <v-list-item three-line>
      <v-list-item-content>
        <div class="text-overline mb-4" v-if="applicant.alias">
          <v-icon>mdi-check-decagram-outline</v-icon> {{ applicant.alias }}
        </div>
        <v-list-item-title class="text-h5 mb-1">
          {{ applicant.name }}
        </v-list-item-title>
        <v-list-item-subtitle>
          Degree: {{ applicant.degree }} <br />
          Invitation State: {{ applicant.invitation_state }}
          <v-icon v-if="applicant.invitation_state === 'completed'" small>
            check_circle
          </v-icon>
        </v-list-item-subtitle>
      </v-list-item-content>

      <v-list-item-avatar tile size="50">
        <v-avatar x-large color="rgba(0, 160, 144)">
          <v-icon dark>mdi-account</v-icon>
        </v-avatar>
      </v-list-item-avatar>
    </v-list-item>

    <v-card-actions>
      <v-btn
        outlined
        rounded
        text
        :disabled="!applicant.alias"
        @click.prevent="createInvitation(applicant)"
      >
        Invite
      </v-btn>

      <v-btn
        outlined
        rounded
        text
        :disabled="applicant.invitation_state !== 'completed'"
        @click.prevent="createInvitation(applicant)"
      >
        Request Credential
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { mapActions, mapMutations } from 'vuex';

export default {
  name: 'ApplicantCard',
  props: {
    applicant: {
      type: Object,
      required: true,
    },
  },
  methods: {
    ...mapMutations('acme', ['SET_SELECTED_APPLICANT']),
    ...mapActions('acme', ['createInvitation']),
  },
};
</script>
