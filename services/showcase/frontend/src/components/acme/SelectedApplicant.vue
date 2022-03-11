<template>
  <div>
    <v-card class="mx-auto" tile outlined>
      <v-app-bar dark color="rgba(0, 160, 144)" elevation="0">
        <v-toolbar-title>Job Applicant</v-toolbar-title>

        <v-spacer></v-spacer>

        <v-btn icon @click="SET_SELECTED_APPLICANT(null)">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-app-bar>

      <v-card-text>
        <p class="text-center">
          <v-avatar x-large color="rgba(0, 160, 144)">
            <v-icon dark>mdi-account</v-icon>
          </v-avatar>
        </p>
        <h2 class="text-center">{{ selectedApplicant.name }}</h2>
        <p class="text-center">{{ selectedApplicant.degree }}</p>
        <p class="text-center" v-if="selectedApplicant.alias">
          <v-icon small>mdi-check-decagram-outline</v-icon>
          {{ selectedApplicant.alias }}
        </p>
        <p class="text-center">
          <v-icon small>mdi-clock</v-icon>
          {{ selectedApplicant.created_at | formatDate }}
        </p>
        <v-divider />
        <p class="mt-6">
          Invitation State: {{ selectedApplicant.invitation_state }}
        </p>
        <p>Connection ID: {{ selectedApplicant.connection_id }}</p>
        <p>Wallet ID: {{ selectedApplicant.wallet_id }}</p>
        <p>Updated At: {{ selectedApplicant.updated_at | formatDateLong }}</p>
        <v-divider />
        <v-expansion-panels flat>
          <v-expansion-panel>
            <v-expansion-panel-header> Details </v-expansion-panel-header>
            <v-expansion-panel-content>
              <pre>{{ JSON.stringify(selectedApplicant, 0, 2) }}</pre>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { mapMutations, mapGetters } from 'vuex';

export default {
  name: 'SelectedApplicant',
  computed: {
    ...mapGetters('acme', ['selectedApplicant']),
  },
  methods: {
    ...mapMutations('acme', ['SET_SELECTED_APPLICANT']),
  },
};
</script>
