<template>
  <div class="applicants-list">
    <h3 class="mb-3">
      Job Applicants ({{ currentSandbox.applicants.length }})
    </h3>
    <v-row>
      <v-col v-for="appl in currentSandbox.applicants" :key="appl.id" cols="4">
        <v-card
          class="mx-auto"
          outlined
          tile
          @click="SET_SELECTED_APPLICANT(appl)"
        >
          <v-system-bar color="rgba(0, 160, 144)" />
          <v-list-item three-line>
            <v-list-item-content>
              <div class="text-overline mb-4" v-if="appl.alias">
                <v-icon>mdi-check-decagram-outline</v-icon> {{ appl.alias }}
              </div>
              <v-list-item-title class="text-h5 mb-1">
                {{ appl.name }}
              </v-list-item-title>
              <v-list-item-subtitle>
                Degree: {{ appl.degree }} <br />
                Invitation State: {{ appl.invitation_state }} <br />
              </v-list-item-subtitle>
            </v-list-item-content>

            <v-list-item-avatar tile size="50">
              <v-avatar x-large color="rgba(0, 160, 144)">
                <v-icon dark>mdi-account</v-icon>
              </v-avatar>
            </v-list-item-avatar>
          </v-list-item>

          <v-card-actions>
            <v-btn outlined rounded text :disabled="!appl.alias" @click.prevent="createInvitation(appl)">
              Invite
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { mapActions, mapMutations, mapGetters } from 'vuex';

export default {
  name: 'Applicants',
  data() {
    return {
      selectedApplicant: {},
    };
  },
  computed: {
    ...mapGetters('acme', ['tenant']),
    ...mapGetters('sandbox', ['currentSandbox']),
  },
  methods: {
    ...mapMutations('acme', ['SET_SELECTED_APPLICANT']),
    ...mapActions('acme', ['createInvitation']),
  },
};
</script>
