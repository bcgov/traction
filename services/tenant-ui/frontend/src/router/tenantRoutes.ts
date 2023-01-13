// Main dashboard
import Dashboard from '@/views/Dashboard.vue';
import About from '@/views/About.vue';
// Tenant
import TenantUi from '@/views/TenantUi.vue';
import Profile from '@/views/tenant/Profile.vue';
import Settings from '@/views/tenant/Settings.vue';
import Developer from '@/views/tenant/Developer.vue';
// Connections
import MyContacts from '@/views/connections/MyContacts.vue';
import MyInvitations from '@/views/connections/MyInvitations.vue';
// Issuance
import MyIssuedCredentials from '@/views/issuance/MyIssuedCredentials.vue';
import Schemas from '@/views/issuance/Schemas.vue';
// // Verifictation
import MyPresentations from '@/views/verification/MyPresentations.vue';
import PresentationTemplates from '@/views/verification/PresentationTemplates.vue';
// // Holder
import MyHeldCredentials from '@/views/holder/MyHeldCredentials.vue';

// Messages
import MyMessages from '@/views/messages/MyMessages.vue';

const tenantRoutes = [
  // Tenant Routes (base / is Tenant side for this app)
  {
    path: '/',
    name: 'TenantUi',
    component: TenantUi,
    children: [
      // Blank route uses dashboard view
      { path: '', name: 'Dashboard', component: Dashboard },

      // About
      {
        path: '/about',
        name: 'About',
        component: About,
      },

      // Tenant - Setup etc
      {
        path: '/tenant/',
        children: [
          {
            path: 'profile',
            name: 'Profile',
            component: Profile,
          },
          {
            path: 'settings',
            name: 'Settings',
            component: Settings,
          },
          {
            path: 'developer',
            name: 'Developer',
            component: Developer,
          },
        ],
      },

      // Tenant - Connections
      {
        path: '/connections/',
        children: [
          {
            path: '',
            name: 'MyContacts',
            component: MyContacts,
          },
          {
            path: 'invitations',
            name: 'MyInvitations',
            component: MyInvitations,
          },
        ],
      },

      // Tenant - Schemas, templates etc
      {
        path: '/configuration/',
        children: [
          {
            path: 'schemas',
            name: 'Schemas',
            component: Schemas,
          },
          {
            path: 'presentationTemplates',
            name: 'PresentationTemplates',
            component: PresentationTemplates,
          },
        ],
      },

      // Tenant - Issuer
      {
        path: '/issuance/',
        children: [
          {
            path: 'credentials',
            name: 'MyIssuedCredentials',
            component: MyIssuedCredentials,
          },
        ],
      },

      // Tenant - Verifier
      {
        path: '/verification/',
        children: [
          {
            path: 'verifications',
            name: 'MyPresentations',
            component: MyPresentations,
          },
        ],
      },

      // Tenant - Holder
      {
        path: '/holder/',
        children: [
          {
            path: 'credentials',
            name: 'MyHeldCredentials',
            component: MyHeldCredentials,
          },
        ],
      },

      // Tenant - Messages
      {
        path: '/messages',
        children: [
          {
            path: 'recent',
            name: 'MyMessages',
            component: MyMessages,
          },
        ],
      },
    ],
  },
];

export default tenantRoutes;
