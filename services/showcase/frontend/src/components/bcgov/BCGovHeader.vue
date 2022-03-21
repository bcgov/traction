<template>
  <header class="gov-header">
    <!-- header for browser print only -->
    <v-toolbar color="#003366" flat class="px-md-12 d-print-none">
      <!-- Navbar content -->
      <a
        href="https://www2.gov.bc.ca"
        data-test="btn-header-logo"
        v-if="this.$vuetify.theme.dark"
      >
        <v-img
          alt="B.C. Government Logo"
          class="d-none d-sm-flex d-md-none"
          contain
          height="3.5rem"
          src="@/assets/images/bc_logo_square.svg"
          width="3.5rem"
        />
        <v-img
          alt="B.C. Government Logo"
          class="d-none d-md-flex"
          contain
          height="3.5rem"
          src="@/assets/images/bc_logo.svg"
          width="10rem"
        />
      </a>
      <h1
        data-test="btn-header-title"
        class="font-weight-bold text-h6 d-flex pl-4"
      >
        {{ appTitle }}
      </h1>
      <v-spacer />
      <p class="session-text" v-if="currentSandbox">
        Current Sandbox Session: <strong>{{ currentSandbox.tag }}</strong>
      </p>
    </v-toolbar>
  </header>
</template>

<script>
import { mapGetters } from 'vuex';
import PrintLogo from '@/assets/images/bc_logo_print.svg';

export default {
  name: 'BCGovHeader',
  data() {
    return {
      PrintLogo: PrintLogo,
    };
  },
  computed: {
    ...mapGetters('sandbox', ['currentSandbox']),
    appTitle() {
      return this.$route && this.$route.meta && this.$route.meta.title
        ? this.$route.meta.title
        : process.env.VUE_APP_TITLE;
    },
  },
};
</script>

<style lang="scss" scoped>
.gov-header {
  @media not print {
    border-bottom: 2px solid #fcba19;
  }
  .text-h6 {
    font-family: inherit !important;
    color: #ffffff;
    overflow: hidden;
    margin-bottom: 0;
  }
  p.session-text {
    font-family: inherit !important;
    color: #ffffff;
    margin-bottom: 0;
    font-size: 0.8em;
  }
}
</style>
