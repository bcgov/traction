<template>
  <v-container>
    <v-row class="text-center">
      <v-col cols="12">
        <v-img
          v-if="this.$vuetify.theme.dark"
          src="@/assets/images/traction_logo_bcgov.svg"
          class="my-3"
          contain
          height="300"
        />
        <v-img
          v-else
          src="@/assets/images/traction_logo.svg"
          class="my-3"
          contain
          height="300"
        />
      </v-col>

      <v-col class="mb-4">
        <h1 class="text-h3 font-weight-bold mb-3">
          <span v-if="this.$vuetify.theme.dark">Digital Trust</span> Traction
          Showcase App
        </h1>

        <p class="subheading font-weight-regular">
          The showcase app is a demonstration of how multiple line-of-business
          applications can integrate with the Traction product.
          <br />This app is not part of the Traction product but can be run
          alongside as a reference.
        </p>
      </v-col>

      <v-col class="mb-5" cols="12">
        <h2 class="text-h5 font-weight-bold mb-3">Traction Resources</h2>

        <v-row justify="center">
          <a
            href="https://github.com/bcgov/traction"
            class="subheading mx-3"
            target="_blank"
          >
            Traction Github
          </a>
          <a
            href="https://github.com/bcgov/traction/blob/develop/docs/ARCHITECTURE.md"
            class="subheading mx-3"
            target="_blank"
          >
            Architecture
          </a>
          <a href="/api/docs" class="subheading mx-3" target="_blank">
            Showcase API Spec
          </a>
        </v-row>
      </v-col>

      <v-col class="mb-5" cols="12">
        <h2 class="text-h5 font-weight-bold mb-3">Ecosystem</h2>
        <a
          href="https://www.hyperledger.org/use/aries"
          class="subheading mx-3"
          target="_blank"
        >
          Hyperledger Aries
        </a>
        <a
          href="https://github.com/hyperledger/aries-cloudagent-python"
          class="subheading mx-3"
          target="_blank"
        >
          ACA-Py Github
        </a>
      </v-col>


      <v-col class="mb-5" cols="12" v-if="this.$vuetify.theme.dark">
        <h2 class="text-h5 font-weight-bold mb-3">Digital Trust Team</h2>
        <a
          href="https://bcgov.github.io/mines-digital-trust/"
          class="subheading mx-3"
          target="_blank"
        >
          Mines Digital Trust page
        </a>
        <a
          href="https://apps.nrs.gov.bc.ca/int/confluence/display/DIGITRUST"
          class="subheading mx-3"
          target="_blank"
        >
          Confluence
        </a>
        <a
          href="https://bcgov.github.io/mines-digital-trust/team.html"
          class="subheading mx-3"
          target="_blank"
        >
          Contact
        </a>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'HelloWorld',

  data: () => ({
    ecosystem: [
      {
        text: 'vuetify-loader',
        href: 'https://github.com/vuetifyjs/vuetify-loader',
      },
      {
        text: 'github',
        href: 'https://github.com/vuetifyjs/vuetify',
      },
      {
        text: 'awesome-vuetify',
        href: 'https://github.com/vuetifyjs/awesome-vuetify',
      },
    ],
    importantLinks: [
      {
        text: 'Documentation',
        href: 'https://vuetifyjs.com',
      },
      {
        text: 'Chat',
        href: 'https://community.vuetifyjs.com',
      },
      {
        text: 'Made with Vuetify',
        href: 'https://madewithvuejs.com/vuetify',
      },
      {
        text: 'Twitter',
        href: 'https://twitter.com/vuetifyjs',
      },
      {
        text: 'Articles',
        href: 'https://medium.com/vuetify',
      },
    ],
  }),
};
</script>
