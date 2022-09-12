<!-- Used to display presentation received after RFC-0037 Present-Proof-v1.0

 https://github.com/hyperledger/aries-rfcs/blob/main/features/0037-present-proof/README.md
 
 May work for RFC-0454 Present-Proof-v2.0, to be tested later.... and update this comment

 https://github.com/hyperledger/aries-rfcs/blob/main/features/0454-present-proof-v2/README.md
 -->

<template>
  <div v-if="presentation">
    <ul>
      <div v-if="props.header">
        <li>Status: {{ presentation.status }}</li>
        <li>Updated at: {{ formatDateLong(presentation.updated_at) }}</li>
        <li>Contact Alias: {{ presentation.contact.alias }}</li>
        <hr />
      </div>
      <!-- VERIFIED Meaning-->
      <div
        v-if="props.showInformation && presentation.status == 'verified'"
        class="information"
      >
        <span class="pi pi-check"></span
        ><span
          >Credential is held by
          <strong>{{ presentation.contact.alias }}</strong></span
        ><br />
        <span class="pi pi-check"></span><span>Credential is valid</span><br />
        <span class="pi pi-check"></span><span>Credential is tamper-free </span
        ><br />
        <span class="pi pi-check"></span
        ><span>All attribute restrictions were satisfied</span><br />
      </div>
      <hr />
      <DataTable
        :value="attribute_claim_rows()"
        responsive-layout="scroll"
        striped-rows
        class="p-datatable-sm"
      >
        <Column field="checkmark" header="" style="width: 30px">
          <template #body="row">
            <span v-if="row.data.checkmark" class="pi pi-check"></span>
          </template>
        </Column>
        <Column field="name" header="Name"></Column>
        <Column field="val" header="Value"></Column>
        <Column field="tooltip" style="width: 40px">
          <template #body="row">
            <InfoModal
              :object="row.data.restrictions"
              :header="'Restrictions'"
            />
          </template>
        </Column>
      </DataTable>

      <br />
      <!-- Identifiers -->
      <Accordion>
        <AccordionTab
          v-for="(item, index) in props.presentation.acapy.presentation_exchange
            .presentation.identifiers"
          :key="index"
          :header="`Identifier_${index + 1}`"
        >
          <ul>
            <li v-for="(val, attr_name, i) in item" :key="i">
              <strong>{{ attr_name }}</strong> : {{ val }}
            </li>
          </ul>
        </AccordionTab>
      </Accordion>
    </ul>
    <Accordion>
      <AccordionTab header="View Raw Content">
        <vue-json-pretty :data="presentation" />
      </AccordionTab>
    </Accordion>
  </div>
  <div v-else>...loading</div>
</template>

<script setup lang="ts">
import { PropType } from 'vue';
import { formatDateLong } from '@/helpers';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import VueJsonPretty from 'vue-json-pretty';
import 'vue-json-pretty/lib/styles.css';
import InfoModal from '../common/InfoModal.vue';

const props = defineProps({
  presentation: {
    type: Object as PropType<any>,
    required: true,
  },
  header: {
    type: Boolean as PropType<boolean>,
    required: false,
    default: true,
  },
  showInformation: {
    type: Boolean as PropType<boolean>,
    required: false,
    default: false,
  },
});

interface AttrbiuteClaimRow {
  name: string;
  val: string;
  attr_type: string;
  referent: string;
  checkmark: boolean;
  restrictions: object;
}

const attribute_claim_rows = (): AttrbiuteClaimRow[] => {
  const pres = props.presentation;
  const result: AttrbiuteClaimRow[] = [];

  //normalize attribute_groups for table
  for (const [k, v] of Object.entries(requested_attribute_groups())) {
    // @ts-expect-error types have not been defined for this object
    v.names.forEach((name: string) => {
      result.push({
        name: name,
        val: pres.acapy.presentation_exchange.presentation.requested_proof
          .revealed_attr_groups[k].values[name].raw,
        attr_type: 'requested_attribute_group',
        referent: k,
        checkmark: true,
        // @ts-expect-error types have not been defined for this object
        restrictions: v.restrictions,
      });
    });
  }
  //normalize single_attributes for table
  for (const [k, v] of Object.entries(requested_single_attributes())) {
    result.push({
      // @ts-expect-error types have not been defined for this object
      name: v.name,
      val: pres.acapy.presentation_exchange.presentation.requested_proof
        .revealed_attrs[k].raw,
      attr_type: 'requested_single_attribute',
      referent: k,
      checkmark: true,
      // @ts-expect-error types have not been defined for this object
      restrictions: v.restrictions,
    });
  }
  //normalize self_attested_attributes for table
  for (const [k, v] of Object.entries(requested_self_attested_attributes())) {
    result.push({
      // @ts-expect-error types have not been defined for this object
      name: v.name,
      val: pres.acapy.presentation_exchange.presentation.requested_proof
        .self_attested_attrs[k],
      attr_type: 'self_attested_attribute',
      referent: k,
      checkmark: false,
      restrictions: { info: 'No Restrictions' },
    });
  }

  // normalize requested_predicates for table
  // ag_rows = requested_attribute_groups().map(ua => console.log(ua)
  return result;
};
// four different payload locations for the provided claims based on these filters.
const requested_attribute_groups = (): any => {
  return Object.fromEntries(
    Object.entries(
      props.presentation.acapy.presentation_exchange.presentation_request
        .requested_attributes
    ).filter(([key, ra]: [string, any]): any => {
      return 'names' in ra && 'restrictions' in ra;
    })
  );
};

const requested_single_attributes = (): any => {
  return Object.fromEntries(
    Object.entries(
      props.presentation.acapy.presentation_exchange.presentation_request
        .requested_attributes
    ).filter(([key, ra]: [string, any]): any => {
      return 'name' in ra && 'restrictions' in ra;
    })
  );
};

const requested_self_attested_attributes = (): any => {
  return Object.fromEntries(
    Object.entries(
      props.presentation.acapy.presentation_exchange.presentation_request
        .requested_attributes
    ).filter(([key, ra]) => {
      // @ts-expect-error types have not been defined for this object
      return 'name' in ra && !('restrictions' in ra);
    })
  );
};

// const requested_predicates_attributes = ():any => {
//   return props.presentation.acapy.presentation_exchange.presentation_request
//     .requested_predicates;
// };
</script>

<style>
.presentation-attr-value {
  padding-left: 1em;
}

.information .pi.pi-check {
  font-size: 18px;
  color: green;
  margin-right: 5px;
}
</style>
