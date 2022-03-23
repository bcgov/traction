<template>
  <v-footer class="traction-footer d-print-none">
    <div v-if="this.$vuetify.theme.dark">
      <v-btn text id="footer-home" href="https://www.gov.bc.ca/">
        <span>Home</span>
      </v-btn>
      <v-btn
        text
        id="footer-about"
        href="https://www2.gov.bc.ca/gov/content/about-gov-bc-ca"
      >
        <span>About gov.bc.ca</span>
      </v-btn>
      <v-btn text id="footer-disclaimer" href="http://gov.bc.ca/disclaimer">
        <span>Disclaimer</span>
      </v-btn>
      <v-btn text id="footer-privacy" href="http://gov.bc.ca/privacy">
        <span>Privacy</span>
      </v-btn>
      <v-btn
        text
        id="footer-accessibility"
        href="http://gov.bc.ca/webaccessibility"
      >
        <span>Accessibility</span>
      </v-btn>
      <v-btn text id="footer-copyright" href="http://gov.bc.ca/copyright">
        <span>Copyright</span>
      </v-btn>
      <v-btn
        text
        id="footer-contact"
        href="https://www2.gov.bc.ca/gov/content/home/contact-us"
      >
        <span>Contact Us</span>
      </v-btn>
    </div>
    <div v-else>
      <a href="https://github.com/bcgov/traction" target="_blank">
        <v-btn class="ma-2" color="white" text icon>
          <v-icon x-large> mdi-github </v-icon>
        </v-btn>
      </a>
    </div>
    <v-spacer />
    <v-switch
      v-model="$vuetify.theme.dark"
      color="white"
      persistent-hint
    />
    <span class="switch-txt">BC Theme</span>
  </v-footer>
</template>

<script>
export default {
  name: 'AppFooter',
};
</script>

<style lang="scss" scoped>
.traction-footer {
  background-color: var(--v-themeBg-base) !important;
  border-top: 3px solid var(--v-themeAccent-base);
  flex-shrink: 0;
  min-height: 2.5rem;
  min-width: 100%;
  padding-bottom: 0;
  padding-top: 0;

  a {
    color: #ffffff;
    font-size: 1rem;
    &:focus {
      outline: none;
    }
    text-decoration: none;
  }

  .v-btn__content > span {
    color: #ffffff;
    font-size: 1rem;
    font-weight: normal;
    text-decoration: none;
    text-transform: none;
  }

  .switch-txt {
    color: whitesmoke !important;
  }
}
</style>
