<template>
  <div v-if="presentation.status == 'verified'">
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
          <InfoModal :object="row.data.restrictions" :header="'Restrictions'" />
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
            <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
            <strong>{{ attr_name }}</strong> : {{ val }}
          </li>
        </ul>
      </AccordionTab>
    </Accordion>
  </div>
  <div v-else>
    {{ $t('verifier.presentationShouldHaveStatus') }}
  </div>
</template>

<script setup lang="ts">
import { PropType } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import InfoModal from '../common/InfoModal.vue';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';

const props = defineProps({
  presentation: {
    type: Object as PropType<any>,
    required: true,
  },
});

interface AttributeClaimRow {
  name: string;
  val: string;
  attr_type: string;
  referent: string;
  checkmark: boolean;
  restrictions: object;
}

const attribute_claim_rows = (): AttributeClaimRow[] => {
  const pres = props.presentation;
  const result: AttributeClaimRow[] = [];

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
