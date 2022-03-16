<template>
  <div class="students-list">
    <h2 class="my-4">Registered Student List</h2>
    <!-- table header -->
    <v-data-table
      :headers="headers"
      item-key="id"
      :items="students"
      disable-sort
      disable-pagination
      hide-default-footer
      :loading="loadingStudents"
    >
      <template #[`item.name`]="{ item }">
        {{ item.name }}
        <v-tooltip bottom v-if="item.wallet_id">
          <template v-slot:activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on">
              <v-icon color="#173840">mdi-wallet</v-icon>
            </span>
          </template>
          <span>{{ item.name }} has a wallet registered in our system</span>
        </v-tooltip>
      </template>
      <template #[`item.actions`]="{ item }">
        <!-- Invite user -->
        <v-tooltip bottom>
          <template #activator="{ on, attrs }">
            <v-btn
              @click="inviteStudent(item)"
              :disabled="!item.wallet_id"
              large
              icon
              v-bind="attrs"
              v-on="on"
            >
              <v-icon>person_add</v-icon>
            </v-btn>
          </template>
          <span>Send an Invitation</span>
        </v-tooltip>

        <!-- Issue Credential -->
        <v-tooltip bottom>
          <template #activator="{ on, attrs }">
            <v-btn
              @click="issueDegree(item)"
              :disabled="!tenant.public_did || !item.wallet_id"
              large
              icon
              v-bind="attrs"
              v-on="on"
            >
              <v-icon>mdi-certificate</v-icon>
            </v-btn>
          </template>
          <span>Issue a Degree Credential</span>
        </v-tooltip>

        <!-- View details -->
        <v-tooltip bottom>
          <template #activator="{ on, attrs }">
            <v-btn
              @click="showStudentDetails(item)"
              large
              icon
              v-bind="attrs"
              v-on="on"
            >
              <v-icon>visibility</v-icon>
            </v-btn>
          </template>
          <span>View Student Details</span>
        </v-tooltip>
      </template>
    </v-data-table>

    <!-- Dialog to show raw json -->
    <v-dialog v-model="studentDialog" width="800">
      <v-card>
        <v-card-title class="text-h5 grey lighten-2">
          Student Details
        </v-card-title>

        <v-card-text>
          <pre>{{ JSON.stringify(selectedStudent, 0, 2) }}</pre>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="studentDialog = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'Students',
  data() {
    return {
      headers: [
        { text: 'Student', align: 'start', value: 'name' },
        {
          text: '',
          align: 'end',
          value: 'actions',
          filterable: false,
          sortable: false,
        },
      ],
      loadingStudents: true,
      selectedStudent: {},
      studentDialog: false,
    };
  },
  computed: {
    ...mapGetters('faber', ['students', 'tenant']),
    ...mapGetters('sandbox', ['currentSandbox']),
  },
  methods: {
    ...mapActions('faber', ['getStudents', 'inviteStudent', 'issueDegree']),
    showStudentDetails(student) {
      this.selectedStudent = student;
      this.studentDialog = true;
    },
  },
  async mounted() {
    await this.getStudents();
    this.loadingStudents = false;
  },
};
</script>

<style lang="scss">
.students-list {
  .v-data-table {
    table {
      border: 1px solid #173840;
    }
    padding: 0 5em;
    background-color: transparent !important;
    thead {
      background-color: #173840;
      tr th {
        color: white !important;
      }
      tr {
        border: 1px solid red !important;
      }
    }
  }
}
tbody {
  tr:hover {
    background-color: transparent !important;
  }
}
</style>

