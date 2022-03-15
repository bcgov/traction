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
        <v-col cols="4" lg="2">
          <Sidebar />
        </v-col>
        <v-col cols="8" lg="7"> <Applicants /></v-col>
        <v-col cols="6" lg="3">
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
import { mapActions, mapGetters } from 'vuex';

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
    async refreshAcme() {
      this.loading = true;
      this.refreshLob();
      this.loading = false;
    },
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
