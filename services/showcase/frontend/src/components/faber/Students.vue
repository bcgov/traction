<template>
  <div class="students-list">
    <h2 class="my-4">Registered Student List</h2>
    <!-- table header -->
    <v-data-table
      class="px-md-16"
      :headers="headers"
      item-key="id"
      :items="studentList"
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
              :disabled="!item.wallet_id || item.connection_id"
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
        <v-tooltip bottom v-if="!item.credential">
          <template #activator="{ on, attrs }">
            <v-btn
              @click="issueDegree(item)"
              :disabled="!tenant.public_did || !item.wallet_id || !item.connection_id"
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

        <!-- View Issued Credential -->
        <v-tooltip bottom v-if="item.credential">
          <template #activator="{ on, attrs }">
            <v-btn
              @click="viewDegreeDetails(item)"
              large
              icon
              v-bind="attrs"
              v-on="on"
            >
              <v-icon v-if="credentialRevoked(item)" color="rgba(200, 060, 74)">mdi-certificate-outline</v-icon>
              <v-icon v-else>mdi-certificate-outline</v-icon>
            </v-btn>
          </template>
          <span v-if="credentialRevoked(item)">View Revoked Credential</span>
          <span v-else>View Issued Credential</span>
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
    <!-- Dialog to show issued degree -->
    <v-dialog v-model="degreeDialog" width="800">
      <v-card>
        <v-card-title class="text-h5 grey lighten-2">
          Degree Details
        </v-card-title>

        <v-card-text>
          <pre>{{ JSON.stringify(selectedCredential, 0, 2) }}</pre>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn v-if="canRevokeCredential(selectedCredential)" color="secondary" text @click="revokeStudentDegree()">
            Revoke
          </v-btn>
          <v-btn color="primary" text @click="degreeDialog = false">
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
      selectedCredential: {},
      degreeDialog: false,
    };
  },
  computed: {
    ...mapGetters('faber', ['students', 'tenant', 'issuedCredentials']),
    ...mapGetters('sandbox', ['currentSandbox']),
    credentialList() {
      const credentials = this.issuedCredentials.map((cred) => {
        // transforming the raw traction data to something reasonable
        // TODO: update traction api responses to be business friendly
        const c = cred.credential;
        const w = cred.workflow;
        const credential = JSON.parse(c.credential);
        const data = {};
        credential.attributes.forEach((attr) => {
          data[attr.name] = attr.value;
        });
        return {
          'id': c.id,
          'cred_def_id': c.cred_def_id,
          'data': data,
          'revocable': c.rev_reg_id !== null,
          'issue_state': c.issue_state,
          'workflow_state': w.workflow_state,
          'created_at': c.created_at,
          'updated_at': c.updated_at
        };
      });
      return credentials;
    },
    studentList() {
      const items = this.students.map((stu) => {
        let item = {...stu};
        item.credential = this.credentialList.find((c)=> c.data.student_id === item.student_id) !== undefined;
        return item;
      });
      return items;
    }
  },
  methods: {
    ...mapActions('faber', ['getStudents', 'inviteStudent', 'issueDegree', 'getIssuedCredentials', 'revokeDegree', 'refreshLob']),
    showStudentDetails(student) {
      this.selectedStudent = student;
      this.studentDialog = true;
    },
    viewDegreeDetails(student) {
      this.selectedStudent = student;
      this.selectedCredential = this.credentialList.find((c)=> c.data.student_id === student.student_id);
      this.degreeDialog = true;
    },
    async revokeStudentDegree() {
      await this.revokeDegree(this.selectedStudent);
      this.degreeDialog = false;
    },
    credentialRevoked(student) {
      const c = this.credentialList.find((c)=> c.data.student_id === student.student_id);
      const result = c ? c.issue_state == 'credential_revoked' : false;
      return result;
    },
    canRevokeCredential(cred) {
      return cred.revocable && cred.issue_state == 'credential_acked' && cred.workflow_state == 'completed';
    }
  },
  async mounted() {
    await this.getStudents();
    await this.getIssuedCredentials();
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

