<template>
  <div class="acme-portal">
    <Header @refresh="refreshAcme" />
    <v-container fluid v-if="currentSandbox">
      <div v-if="loading" class="text-center">
        <v-progress-circular
          indeterminate
          size="100"
          v-if="loading"
          color="primary"
        />
      </div>
      <v-row v-else>
        <v-col cols="12" sm="4" md="3" lg="2">
          <Sidebar />
        </v-col>
        <v-col cols="12" sm="8" md="" lg="7"> <Applicants /></v-col>
        <v-col cols="12" md="5" lg="3">
          <SelectedApplicant v-if="selectedApplicant" />
        </v-col>
      </v-row>
    </v-container>
    <div v-else>
      <p class="ma-10">
        No sandbox session set, please go to Innkeeper tab to set that up
      </p>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapMutations } from 'vuex';

import Applicants from '@/components/acme/Applicants.vue';
import Header from '@/components/acme/Header.vue';
import SelectedApplicant from '@/components/acme/SelectedApplicant.vue';
import Sidebar from '@/components/acme/Sidebar.vue';

export default {
  name: 'Acme',
  components: { Applicants, Header, SelectedApplicant, Sidebar },
  data() {
    return {
      loading: false,
    };
  },
  computed: {
    ...mapGetters('sandbox', ['currentSandbox']),
    ...mapGetters('acme', ['selectedApplicant']),
  },
  methods: {
    ...mapActions('acme', ['refreshLob']),
    ...mapMutations('acme', ['SET_SELECTED_APPLICANT']),
    async refreshAcme() {
      this.loading = true;
      await this.refreshLob();
      this.loading = false;
    },
  },
  mounted () {
    this.SET_SELECTED_APPLICANT(null);
  },
};
</script>

<style lang="scss">
.acme-portal {
  height: 100%;
  font-family: 'Helvetica' !important;
  background-color: whitesmoke !important;
}
</style>
