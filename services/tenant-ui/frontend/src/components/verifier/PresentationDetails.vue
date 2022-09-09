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
      <div v-if="props.showInformation && presentation.status == 'verified'">
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
      <!-- PRESENTATION RECEIVED-->

      <DataTable :value="attribute_claim_rows()" responsiveLayout="scroll">
        <Column field="name" header="Name"></Column>
        <Column field="val" header="Value"></Column>
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
  tooltip: object;
}

const attribute_claim_rows = (): AttrbiuteClaimRow[] => {
  const pres = test_presentation;
  let result: AttrbiuteClaimRow[] = [];

  //normalize attribute_groups for table
  for (const [k, v] of Object.entries(requested_attribute_groups())) {
    v.names.forEach((name) => {
      result.push({
        name: name,
        val: pres.acapy.presentation_exchange.presentation.requested_proof
          .revealed_attr_groups[k].values[name].raw,
        attr_type: 'requested_attribute_group',
        referent: k,
        tooltip: '',
      });
    });
  }
  //normalize single_attributes for table
  for (const [k, v] of Object.entries(requested_single_attributes())) {
    result.push({
      name: v.name,
      val: pres.acapy.presentation_exchange.presentation.requested_proof
        .revealed_attrs[k].raw,
      attr_type: 'requested_single_attribute',
      referent: k,
      tooltip: '',
    });
  }
  //normalize self_attested_attributes for table
  for (const [k, v] of Object.entries(requested_self_attested_attributes())) {
    result.push({
      name: v.name,
      val: pres.acapy.presentation_exchange.presentation.requested_proof
        .self_attested_attrs[k],
      attr_type: 'self_attested_attribute',
      referent: k,
      tooltip: '',
    });
  }

  // normalize requested_predicates for table
  // ag_rows = requested_attribute_groups().map(ua => console.log(ua)
  console.log(result);
  return result;
};
// four different payload locations for the provided claims based on these filters.
const requested_attribute_groups = (): any => {
  return Object.fromEntries(
    Object.entries(
      test_presentation.acapy.presentation_exchange.presentation_request
        .requested_attributes
    ).filter(([key, ra]: [string, any]): any => {
      return 'names' in ra && 'restrictions' in ra;
    })
  );
};

const requested_single_attributes = (): any => {
  return Object.fromEntries(
    Object.entries(
      test_presentation.acapy.presentation_exchange.presentation_request
        .requested_attributes
    ).filter(([key, ra]: [string, any]): any => {
      return 'name' in ra && 'restrictions' in ra;
    })
  );
};

const requested_self_attested_attributes = (): any => {
  return Object.fromEntries(
    Object.entries(
      test_presentation.acapy.presentation_exchange.presentation_request
        .requested_attributes
    ).filter(([key, ra]) => {
      return 'name' in ra && !('restrictions' in ra);
    })
  );
};

const test_presentation = {
  status: 'verified',
  state: 'verified',
  error_status_detail: null,
  deleted: false,
  created_at: '2022-09-01T21:50:18.346052',
  updated_at: '2022-09-01T21:50:48.023481',
  tags: null,
  acapy: {
    presentation_exchange: {
      connection_id: 'ae4264f5-a4cf-4a2d-adac-69abd734a8ed',
      presentation_exchange_id: '3e95f5ac-ee19-47bb-a634-a0736cc2fc9d',
      trace: false,
      presentation_request: {
        nonce: '431497319149026976827721',
        name: 'proof-request',
        version: '1.0',
        requested_attributes: {
          attr_0: {
            names: ['name', 'title'],
            restrictions: [
              {
                cred_def_id: 'VJzV3rYSD64Fefgp5PjH3g:3:CL:446236:test',
              },
            ],
          },
          '0_organizationid_uuid': {
            restrictions: [
              {
                cred_def_id:
                  'G4EPNiVuNCikvrELJrVsxq:3:CL:455019:NB-Verified-Organization-VC',
              },
            ],
            non_revoked: {
              to: 1662069018,
              from: 0,
            },
            name: 'Organization Id',
          },
          '1_organizationname_uuid': {
            restrictions: [
              {
                cred_def_id:
                  'G4EPNiVuNCikvrELJrVsxq:3:CL:455019:NB-Verified-Organization-VC',
              },
            ],
            non_revoked: {
              to: 1662069018,
              from: 0,
            },
            name: 'Organization name',
          },
          '2_organizationemail_uuid': {
            restrictions: [
              {
                cred_def_id:
                  'G4EPNiVuNCikvrELJrVsxq:3:CL:455019:NB-Verified-Organization-VC',
              },
            ],
            non_revoked: {
              to: 1662069018,
              from: 0,
            },
            name: 'Organization email',
          },
          '3_organizationaddress_uuid': {
            restrictions: [
              {
                cred_def_id:
                  'G4EPNiVuNCikvrELJrVsxq:3:CL:455019:NB-Verified-Organization-VC',
              },
            ],
            non_revoked: {
              to: 1662069018,
              from: 0,
            },
            name: 'Organization address',
          },
          '4_companyregistrationid_uuid': {
            restrictions: [
              {
                cred_def_id:
                  'G4EPNiVuNCikvrELJrVsxq:3:CL:455019:NB-Verified-Organization-VC',
              },
            ],
            non_revoked: {
              to: 1662069018,
              from: 0,
            },
            name: 'Company registration Id',
          },
          '5_kyleselfattestedone_uuid': {
            name: 'KyleSelfAttestedOne',
          },
          '6_kyleselfattestedtwo_uuid': {
            name: 'KyleSelfAttestedTwo',
          },
          '7_kyleselfattestedthree_uuid': {
            name: 'KyleSelfAttestedThree',
          },
        },
        requested_predicates: {},
      },
      presentation_proposal_dict: {
        '@type': 'https://didcomm.org/present-proof/1.0/propose-presentation',
        '@id': '80780a91-f8b8-4aec-ba5e-6b8238c12538',
        comment: '',
        presentation_proposal: {
          '@type': 'https://didcomm.org/present-proof/1.0/presentation-preview',
          attributes: [
            {
              name: 'Organization Id',
              cred_def_id:
                'G4EPNiVuNCikvrELJrVsxq:3:CL:455019:NB-Verified-Organization-VC',
            },
            {
              name: 'Organization name',
              cred_def_id:
                'G4EPNiVuNCikvrELJrVsxq:3:CL:455019:NB-Verified-Organization-VC',
            },
            {
              name: 'Organization email',
              cred_def_id:
                'G4EPNiVuNCikvrELJrVsxq:3:CL:455019:NB-Verified-Organization-VC',
            },
            {
              name: 'Organization address',
              cred_def_id:
                'G4EPNiVuNCikvrELJrVsxq:3:CL:455019:NB-Verified-Organization-VC',
            },
            {
              name: 'Company registration Id',
              cred_def_id:
                'G4EPNiVuNCikvrELJrVsxq:3:CL:455019:NB-Verified-Organization-VC',
            },
            {
              name: 'KyleSelfAttestedOne',
            },
            {
              name: 'KyleSelfAttestedTwo',
            },
            {
              name: 'KyleSelfAttestedThree',
            },
          ],
          predicates: [],
        },
      },
      verified: 'true',
      auto_present: false,
      auto_verify: false,
      state: 'verified',
      thread_id: '80780a91-f8b8-4aec-ba5e-6b8238c12538',
      updated_at: '2022-09-01T21:50:47.989456Z',
      initiator: 'external',
      created_at: '2022-09-01T21:50:18.322384Z',
      presentation: {
        proof: {
          proofs: [
            {
              primary_proof: {
                eq_proof: {
                  revealed_attrs: {
                    companyregistrationid: '296465',
                    organizationaddress:
                      '5814183504534705250898893525245189152361086341053167714586391797700349915923',
                    organizationemail:
                      '40688171236625710333953232349493459574358819062886329694757481925740013254700',
                    organizationid: '5',
                    organizationname:
                      '58464213387486291332388039064473705015198621313956412140747522498407952402966',
                  },
                  a_prime:
                    '10149613199217474401834359545317033898160097530028930681531395791296658001713432921899385976969349605846851543289705622265149159237458566373272907743722664130276813806348997590793157422883584539000372780093518480286304676625425034758428409237818118546277251757738007398768576283614428425291763142186429149944992480056065582259599205713422753343854397518386438404695141716382036898635345323309345388084191289710496345647236655699240350433788186782835945575310384554195216735848474033829918277101602305352633121837392953152142855506978698654932307529433618258714491962703505566099686113324675851276663061679073437406417',
                  e: '92776603049079530384455040634105011442889547690435293556592915014520812661152243558010015885505965741605322202096238153200336216753625489',
                  v: '455265523622612699139999291726053297749523880444469528903473665501116464828215714028069671573473169561053586890749229080417450962761087398398208207694763843366050631748818884821050106292989056356727004617743075418329667511494518077933810478494644405550836383874508527841310791472981759909157719530211373457391255162680950484285943785936100290059368503406593131450549047315179918337160589951580536566524574483860501252019240457254300088788415372664603471427310638197359504740373752204582526364189100258374382507408678618873763399884356586634592094232056474609522038653591426273605786200162569797864597843146117755550960501681315579664796279623437074890357970437804002972629423313247970862375100888204555326161011932605061600452080396612154412198216888304339623551692471152546040216899524710533572272370128334372632574972227185790880270015645564878304948324885950235139690799930008279456161928392864194348753517027976382326',
                  m: {
                    master_secret:
                      '12455324169050778344642431641031626707141670171100534405705818444940771458804986132422602022623214215434455143053238735398903813062958668580999287999675157702622066107831802482642',
                  },
                  m2: '1136649362309951524294949106130064230809410844672788324849000717389617520392080490510909167343682485311381700645866408091328592550928098375576281822077115',
                },
                ge_proofs: [],
              },
            },
          ],
        },
        requested_proof: {
          revealed_attrs: {
            '1_organizationname_uuid': {
              sub_proof_index: 0,
              encoded:
                '58464213387486291332388039064473705015198621313956412140747522498407952402966',
              raw: 'Copper Mountain Mining Corp',
            },
            '3_organizationaddress_uuid': {
              sub_proof_index: 0,
              encoded:
                '5814183504534705250898893525245189152361086341053167714586391797700349915923',
              raw: 'BC Canada',
            },
            '0_organizationid_uuid': {
              sub_proof_index: 0,
              encoded: '5',
              raw: '5',
            },
            '4_companyregistrationid_uuid': {
              sub_proof_index: 0,
              encoded: '296465',
              raw: '296465',
            },
            '2_organizationemail_uuid': {
              sub_proof_index: 0,
              encoded:
                '40688171236625710333953232349493459574358819062886329694757481925740013254700',
              raw: 'copper@getairmail.com',
            },
          },
          revealed_attr_groups: {
            attr_0: {
              sub_proof_index: 0,
              values: {
                name: {
                  raw: 'F',
                  encoded:
                    '111485737994509659498044467867576034197262524114183546611539441564110959814825',
                },
                title: {
                  raw: 'z',
                  encoded:
                    '40394220812323521380438532724649039123625828757177904707523121260138750966534',
                },
              },
            },
          },
          self_attested_attrs: {
            '7_kyleselfattestedthree_uuid': 'Bengals',
            '6_kyleselfattestedtwo_uuid': 'Bears',
            '5_kyleselfattestedone_uuid': 'Packers',
          },
          unrevealed_attrs: {},
          predicates: {},
        },
        identifiers: [
          {
            schema_id:
              'G4EPNiVuNCikvrELJrVsxq:2:NB-Verified-Organization-VC:1.0',
            cred_def_id:
              'G4EPNiVuNCikvrELJrVsxq:3:CL:455019:NB-Verified-Organization-VC',
            rev_reg_id:
              'G4EPNiVuNCikvrELJrVsxq:4:G4EPNiVuNCikvrELJrVsxq:3:CL:455019:NB-Verified-Organization-VC:CL_ACCUM:57ddcd99-a5e4-4154-b464-ee2be4210ee7',
            timestamp: 1662047815,
          },
        ],
      },
      role: 'verifier',
    },
  },
  verifier_presentation_id: '5f2ce630-6cea-45aa-9b25-79065b798af5',
  contact: {
    contact_id: '84037a51-cf4f-48e5-9a50-1c7322766b93',
    alias: 'CuMTN on NB Staging',
    external_reference_id: null,
  },
  name: 'proof-request',
  version: '1.0',
  comment: null,
  external_reference_id: null,
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

.pi.pi-check {
  font-size: 18px;
  color: green;
  margin-right: 5px;
}
</style>
