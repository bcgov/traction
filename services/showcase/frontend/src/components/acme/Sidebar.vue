<template>
  <div>
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
  </div>
</template>

<script>
export default {
  name: 'AcmeSidebar',
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
.v-item--active {
  color: rgba(0, 160, 144) !important;
}
</style>
