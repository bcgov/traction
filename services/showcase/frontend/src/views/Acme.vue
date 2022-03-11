<template>
  <div class="acme-portal">
    <v-toolbar dark flat prominent src="@/assets/images/computer.jpg">
      <template v-slot:img="{ props }">
        <v-img
          v-bind="props"
          gradient="to top right, rgba(42,80,82,.5), rgba(0,160,144,.8)"
        ></v-img>
      </template>
      <v-app-bar-nav-icon></v-app-bar-nav-icon>

      <v-toolbar-title><v-icon x-large color="black">mdi-alpha-a-box</v-icon> ACME Corporation HR Portal</v-toolbar-title>

      <v-spacer></v-spacer>

      <v-btn icon>
        <v-icon>mdi-key</v-icon>
      </v-btn>
      <v-btn icon>
        <v-icon>mdi-cube</v-icon>
      </v-btn>
      <v-btn icon>
        <v-icon>mdi-export</v-icon>
      </v-btn>
    </v-toolbar>

    <v-container fluid>
      <v-row>
        <v-col cols="4" lg="2">
          <v-navigation-drawer permanent class="mx-0">
            <v-system-bar color="rgba(42,80,82)" />
            <v-list>
              <v-list-item>
                <v-avatar color="rgba(42,80,82)">
                  <v-icon dark>mdi-account-tie</v-icon>
                </v-avatar>
              </v-list-item>

              <v-list-item link>
                <v-list-item-content>
                  <v-list-item-title class="text-h6">
                    HR Manager 1
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    human.res@acmecorp.com
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <v-divider></v-divider>
            <v-list nav>
              <v-list-item-group v-model="selectedItem" color="primary">
                <v-list-item v-for="(item, i) in items" :key="i">
                  <v-list-item-icon>
                    <v-icon v-text="item.icon"></v-icon>
                  </v-list-item-icon>

                  <v-list-item-content>
                    <v-list-item-title v-text="item.text"></v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-navigation-drawer>
        </v-col>
        <v-col cols="8" lg="10">test</v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'Acme',
  components: {},
  computed: {
    ...mapGetters('sandbox', ['currentSandbox']),
  },
  data: () => ({
    selectedItem: 1,
    items: [
      { text: 'Employees', icon: 'mdi-card-account-details' },
      { text: 'Job Applicants', icon: 'mdi-account-multiple' },
      { text: 'Starred', icon: 'mdi-star' },
      { text: 'Recent', icon: 'mdi-history' },
      { text: 'Offline', icon: 'mdi-check-circle' },
      { text: 'Uploads', icon: 'mdi-upload' },
      { text: 'Backups', icon: 'mdi-cloud-upload' },
    ],
  }),
};
</script>

<style lang="scss" scoped>
.acme-portal {
  height: 100%;
  font-family: 'Helvetica' !important;
  background-color: whitesmoke !important;

  .v-item--active {
    color:rgba(0,160,144) !important;
  }
}
</style>
