import About from '@/views/About.vue';
import Log from '@/views/Log.vue';
// Innkeeper
import InnkeeperUi from '@/views/InnkeeperUi.vue';
import InnkeeperApiKeys from '@/views/innkeeper/InnkeeperApiKeys.vue';
import InnkeeperReservations from '@/views/innkeeper/InnkeeperReservations.vue';
import InnkeeperReservationsHistory from '@/views/innkeeper/InnkeeperReservationsHistory.vue';
import InnkeeperServerConfig from '@/views/innkeeper/InnkeeperServerConfig.vue';
import InnkeeperTenants from '@/views/innkeeper/InnkeeperTenants.vue';

const innkeeperRoutes = [
  {
    path: '/innkeeper/',
    name: 'InnkeeperUi',
    component: InnkeeperUi,
    meta: { isInnkeeper: true },
    children: [
      {
        path: 'tenants',
        name: 'InnkeeperTenants',
        component: InnkeeperTenants,
      },

      // Reservations
      {
        path: 'reservations',
        name: 'InnkeeperReservations',
        component: InnkeeperReservations,
      },
      {
        path: 'reservations/history',
        name: 'InnkeeperReservationsHistory',
        component: InnkeeperReservationsHistory,
      },

      // Authentications
      {
        path: 'authentications/keys',
        name: 'InnkeeperApiKeys',
        component: InnkeeperApiKeys,
      },

      // Authentications
      {
        path: 'server',
        name: 'InnkeeperServerConfig',
        component: InnkeeperServerConfig,
      },

      // About
      {
        path: 'about',
        name: 'InnkeeperAbout',
        component: About,
        meta: { isInnkeeper: true },
      },

      // Log
      {
        path: 'log',
        name: 'InnkeeperLog',
        component: Log,
      },
    ],
  },
];

export default innkeeperRoutes;
