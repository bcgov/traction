<template>
  <div>
    <div v-if="loading" class="text-center">
      <v-progress-circular
        indeterminate
        size="100"
        v-if="loading"
        color="primary"
      />
    </div>
    <div v-else class="applicants-list">
      <h3 class="mb-3">Job Applicants ({{ applicants.length }})</h3>
      <v-row>
        <v-col v-for="appl in applicants" :key="appl.id" cols="4">
          <ApplicantCard :applicant="appl" />
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script>
import { mapActions, mapMutations, mapGetters } from 'vuex';

import ApplicantCard from '@/components/acme/ApplicantCard.vue';

export default {
  name: 'Applicants',
  components: {
    ApplicantCard,
  },
  data() {
    return {
      loading: true,
      selectedApplicant: {},
    };
  },
  computed: {
    ...mapGetters('acme', ['applicants', 'tenant']),
  },
  methods: {
    ...mapMutations('acme', ['SET_SELECTED_APPLICANT']),
    ...mapActions('acme', ['createInvitation', 'getApplicants']),
  },
  async mounted() {
    await this.getApplicants();
    this.loading = false;
  },
};
</script>
