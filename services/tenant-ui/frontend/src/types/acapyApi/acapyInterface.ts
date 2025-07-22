/*
 * ---------------------------------------------------------------
 * ## THIS FILE WAS GENERATED VIA SWAGGER-TYPESCRIPT-API        ##
 * ##                                                           ##
 * ## AUTHOR: acacode                                           ##
 * ## SOURCE: https://github.com/acacode/swagger-typescript-api ##
 * ---------------------------------------------------------------
 */

export interface AMLRecord {
  aml?: Record<string, string>;
  amlContext?: string;
  version?: string;
}

export interface ActionMenuFetchResult {
  /** Action menu */
  result?: Menu;
}

export type ActionMenuModulesResult = object;

export interface AddOcaRecordRequest {
  /** OCA Bundle */
  bundle?: Record<string, any>;
  /**
   * Cred Def identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id?: string;
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id?: string;
  /** (Public) Url for OCA Bundle */
  url?: string;
}

export interface AddProof {
  /** @example {"hello":"world"} */
  document: Record<string, any>;
  /** @example {"cryptosuite":"eddsa-jcs-2022","proofPurpose":"assertionMethod","type":"DataIntegrityProof","verificationMethod":"did:web:example.com#key-01"} */
  options?: DataIntegrityProofOptions;
}

export interface AddProofResponse {
  /** @example {"hello":"world"} */
  secured_document: Record<string, any>;
}

export interface AdminConfig {
  /** Configuration settings */
  config: Record<string, any>;
}

export type AdminMediationDeny = object;

export interface AdminModules {
  /** List of admin modules */
  result?: string[];
}

export type AdminReset = object;

export type AdminShutdown = object;

export interface AdminStatus {
  /** Conductor statistics */
  conductor?: Record<string, any>;
  /** Default label */
  label?: string | null;
  /** Timing results */
  timing?: Record<string, any>;
  /** Version code */
  version?: string;
}

export interface AdminStatusLiveliness {
  /**
   * Liveliness status
   * @example true
   */
  alive?: boolean;
}

export interface AdminStatusReadiness {
  /**
   * Readiness status
   * @example true
   */
  ready?: boolean;
}

export interface AnonCredsPresSpec {
  /** Nested object mapping proof request attribute referents to requested-attribute specifiers */
  requested_attributes: Record<string, AnonCredsRequestedCredsRequestedAttr>;
  /** Nested object mapping proof request predicate referents to requested-predicate specifiers */
  requested_predicates: Record<string, AnonCredsRequestedCredsRequestedPred>;
  /** Self-attested attributes to build into proof */
  self_attested_attributes: Record<string, string>;
  /**
   * Whether to trace event (default false)
   * @example false
   */
  trace?: boolean;
}

export interface AnonCredsPresentationReqAttrSpec {
  /**
   * Attribute name
   * @example "favouriteDrink"
   */
  name?: string;
  /** Attribute name group */
  names?: string[];
  non_revoked?: AnonCredsPresentationReqAttrSpecNonRevoked | null;
  /** If present, credential must satisfy one of given restrictions: specify schema_id, schema_issuer_did, schema_name, schema_version, issuer_did, cred_def_id, and/or attr::<attribute-name>::value where <attribute-name> represents a credential attribute name */
  restrictions?: Record<string, string>[];
}

export interface AnonCredsPresentationReqAttrSpecNonRevoked {
  /**
   * Earliest time of interest in non-revocation interval
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  from?: number;
  /**
   * Latest time of interest in non-revocation interval
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  to?: number;
}

export interface AnonCredsPresentationReqPredSpec {
  /**
   * Attribute name
   * @example "index"
   */
  name: string;
  non_revoked?: AnonCredsPresentationReqPredSpecNonRevoked | null;
  /**
   * Predicate type ('<', '<=', '>=', or '>')
   * @example ">="
   */
  p_type: '<' | '<=' | '>=' | '>';
  /** Threshold value */
  p_value: number;
  /** If present, credential must satisfy one of given restrictions: specify schema_id, schema_issuer_did, schema_name, schema_version, issuer_did, cred_def_id, and/or attr::<attribute-name>::value where <attribute-name> represents a credential attribute name */
  restrictions?: Record<string, string>[];
}

export interface AnonCredsPresentationReqPredSpecNonRevoked {
  /**
   * Earliest time of interest in non-revocation interval
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  from?: number;
  /**
   * Latest time of interest in non-revocation interval
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  to?: number;
}

export interface AnonCredsPresentationRequest {
  /**
   * Proof request name
   * @example "Proof request"
   */
  name?: string;
  non_revoked?: AnonCredsPresentationRequestNonRevoked | null;
  /**
   * Nonce
   * @pattern ^[1-9][0-9]*$
   * @example "1"
   */
  nonce?: string;
  /** Requested attribute specifications of proof request */
  requested_attributes: Record<string, AnonCredsPresentationReqAttrSpec>;
  /** Requested predicate specifications of proof request */
  requested_predicates: Record<string, AnonCredsPresentationReqPredSpec>;
  /**
   * Proof request version
   * @pattern ^[0-9.]+$
   * @example "1.0"
   */
  version?: string;
}

export interface AnonCredsPresentationRequestNonRevoked {
  /**
   * Earliest time of interest in non-revocation interval
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  from?: number;
  /**
   * Latest time of interest in non-revocation interval
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  to?: number;
}

export interface AnonCredsRequestedCredsRequestedAttr {
  /**
   * Wallet credential identifier (typically but not necessarily a UUID)
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_id: string;
  /** Whether to reveal attribute in proof (default true) */
  revealed?: boolean;
}

export interface AnonCredsRequestedCredsRequestedPred {
  /**
   * Wallet credential identifier (typically but not necessarily a UUID)
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_id: string;
  /**
   * Epoch timestamp of interest for non-revocation proof
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  timestamp?: number;
}

export type AnonCredsRevocationModuleResponse = object;

export interface AnonCredsSchema {
  /** Schema attribute names */
  attrNames: string[];
  /**
   * Issuer Identifier of the credential definition or schema
   * @example "did:(method):WgWxqztrNooG92RXvxSTWv"
   */
  issuerId: string;
  /**
   * Schema name
   * @example "Example schema"
   */
  name: string;
  /**
   * Schema version
   * @example "1.0"
   */
  version: string;
}

export interface AttachDecorator {
  /**
   * Attachment identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Byte count of data included by reference
   * @example 1234
   */
  byte_count?: number;
  data: AttachDecoratorData;
  /**
   * Human-readable description of content
   * @example "view from doorway, facing east, with lights off"
   */
  description?: string;
  /**
   * File name
   * @example "IMG1092348.png"
   */
  filename?: string;
  /**
   * Hint regarding last modification datetime, in ISO-8601 format
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  lastmod_time?: string;
  /**
   * MIME type
   * @example "image/png"
   */
  'mime-type'?: string;
}

export interface AttachDecoratorData {
  /**
   * Base64-encoded data
   * @pattern ^[a-zA-Z0-9+/]*={0,2}$
   * @example "ey4uLn0="
   */
  base64?: string;
  /**
   * JSON-serialized data
   * @example "{"sample": "content"}"
   */
  json?: any;
  /** Detached Java Web Signature */
  jws?: AttachDecoratorDataJWS;
  /** List of hypertext links to data */
  links?: string[];
  /**
   * SHA256 hash (binhex encoded) of content
   * @pattern ^[a-fA-F0-9+/]{64}$
   * @example "617a48c7c8afe0521efdc03e5bb0ad9e655893e6b4b51f0e794d70fba132aacb"
   */
  sha256?: string;
}

export interface AttachDecoratorData1JWS {
  header: AttachDecoratorDataJWSHeader;
  /**
   * protected JWS header
   * @pattern ^[-_a-zA-Z0-9]*$
   * @example "ey4uLn0"
   */
  protected?: string;
  /**
   * signature
   * @pattern ^[-_a-zA-Z0-9]*$
   * @example "ey4uLn0"
   */
  signature: string;
}

export interface AttachDecoratorDataJWS {
  header?: AttachDecoratorDataJWSHeader;
  /**
   * protected JWS header
   * @pattern ^[-_a-zA-Z0-9]*$
   * @example "ey4uLn0"
   */
  protected?: string;
  /**
   * signature
   * @pattern ^[-_a-zA-Z0-9]*$
   * @example "ey4uLn0"
   */
  signature?: string;
  /** List of signatures */
  signatures?: AttachDecoratorData1JWS[];
}

export interface AttachDecoratorDataJWSHeader {
  /**
   * Key identifier, in W3C did:key or DID URL format
   * @pattern ^did:(?:key:z[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]+|sov:[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}(;.*)?(\?.*)?#.+)$
   * @example "did:sov:LjgpST2rjsoxYegQDRm7EL#keys-4"
   */
  kid: string;
}

export interface AttachmentDef {
  /**
   * Attachment identifier
   * @example "attachment-0"
   */
  id?: string;
  /**
   * Attachment type
   * @example "present-proof"
   */
  type?: 'credential-offer' | 'present-proof';
}

export interface AttributeMimeTypesResult {
  results?: Record<string, string>;
}

export interface BasicMessageList {
  /** List of basic message records */
  results?: BasicMessageRecord[];
}

export type BasicMessageModuleResponse = object;

export interface BasicMessageRecord {
  connection_id?: string;
  content?: string;
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  locale?: string;
  message_id?: string;
  /**
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  sent_time?: string;
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface Checkin {
  /**
   * The reservation password
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  reservation_pwd: string;
}

export interface CheckinResponse {
  /**
   * Master key used for key derivation.
   * @example "MySecretKey123"
   */
  token?: string;
  /**
   * Subwallet identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  wallet_id: string;
  /**
   * Subwallet identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  wallet_key?: string;
}

export interface ClaimFormat {
  di_vc?: Record<string, any>;
  jwt?: Record<string, any>;
  jwt_vc?: Record<string, any>;
  jwt_vp?: Record<string, any>;
  ldp?: Record<string, any>;
  ldp_vc?: Record<string, any>;
  ldp_vp?: Record<string, any>;
}

export interface ClearPendingRevocationsRequest {
  /** Credential revocation ids by revocation registry id: omit for all, specify null or empty list for all pending per revocation registry */
  purge?: Record<string, string[]>;
}

export interface ConfigurableWriteLedgers {
  /** List of configurable write ledgers identifiers */
  write_ledgers?: string[];
}

export interface ConfigureWebvh {
  /**
   * Auto sign witness requests
   * @example "false"
   */
  auto_attest?: boolean;
  /**
   * Notify watchers on DID updates
   * @example "false"
   */
  notify_watchers?: boolean;
  /**
   * URL of the webvh server
   * @example "http://localhost:8000"
   */
  server_url?: string;
  /**
   * Enable the witness role
   * @example "false"
   */
  witness?: boolean;
  /**
   * An invitation from a witness, required for a controller
   * @example "http://localhost:3000?oob=eyJAdHlwZSI6ICJodHRwczovL2RpZGNvbW0ub3JnL291dC1vZi1iYW5kLzEuMS9pbnZpdGF0aW9uIiwgIkBpZCI6ICJlMzI5OGIyNS1mZjRlLTRhZmItOTI2Yi03ZDcyZmVlMjQ1ODgiLCAibGFiZWwiOiAid2VidmgtZW5kb3JzZXIiLCAiaGFuZHNoYWtlX3Byb3RvY29scyI6IFsiaHR0cHM6Ly9kaWRjb21tLm9yZy9kaWRleGNoYW5nZS8xLjAiXSwgInNlcnZpY2VzIjogW3siaWQiOiAiI2lubGluZSIsICJ0eXBlIjogImRpZC1jb21tdW5pY2F0aW9uIiwgInJlY2lwaWVudEtleXMiOiBbImRpZDprZXk6ejZNa3FDQ1pxNURSdkdMcDV5akhlZlZTa2JhN0tYWlQ1Nld2SlJacEQ2Z3RvRzU0I3o2TWtxQ0NacTVEUnZHTHA1eWpIZWZWU2tiYTdLWFpUNTZXdkpSWnBENmd0b0c1NCJdLCAic2VydmljZUVuZHBvaW50IjogImh0dHA6Ly9sb2NhbGhvc3Q6MzAwMCJ9XX0"
   */
  witness_invitation?: string;
  /**
   * Existing key to use as witness key
   * @example "z6MkgKA7yrw5kYSiDuQFcye4bMaJpcfHFry3Bx45pdWh3s8i"
   */
  witness_key?: string;
}

export interface ConnRecord {
  /**
   * Connection acceptance: manual or auto
   * @example "auto"
   */
  accept?: 'manual' | 'auto';
  /**
   * Optional alias to apply to connection for later use
   * @example "Bob, providing quotes"
   */
  alias?: string;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id: string;
  /**
   * Connection protocol used
   * @example "didexchange/1.1"
   */
  connection_protocol?: 'connections/1.0' | 'didexchange/1.0' | 'didexchange/1.1';
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Error message
   * @example "No DIDDoc provided; cannot connect to public DID"
   */
  error_msg?: string;
  /**
   * Inbound routing connection id to use
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  inbound_connection_id?: string;
  /**
   * Public key for connection
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44}$
   * @example "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
   */
  invitation_key?: string;
  /**
   * Invitation mode
   * @example "once"
   */
  invitation_mode?: 'once' | 'multi' | 'static';
  /**
   * ID of out-of-band invitation message
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  invitation_msg_id?: string;
  /**
   * Our DID for connection
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$|^did:([a-zA-Z0-9_]+)(:[a-zA-Z0-9_.%-]+)?:([a-zA-Z0-9_.%-]+(:[a-zA-Z0-9_.%-]+)*)((;[a-zA-Z0-9_.:%-]+=[a-zA-Z0-9_.:%-]*)*)(\/[^#?]*)?([?][^#]*)?(\#.*)?$$
   * @example "did:peer:WgWxqztrNooG92RXvxSTWv"
   */
  my_did?: string;
  /**
   * Connection request identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  request_id?: string;
  /**
   * State per RFC 23
   * @example "invitation-sent"
   */
  rfc23_state?: string;
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Their DID for connection
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$|^did:([a-zA-Z0-9_]+)(:[a-zA-Z0-9_.%-]+)?:([a-zA-Z0-9_.%-]+(:[a-zA-Z0-9_.%-]+)*)((;[a-zA-Z0-9_.:%-]+=[a-zA-Z0-9_.:%-]*)*)(\/[^#?]*)?([?][^#]*)?(\#.*)?$$
   * @example "did:peer:WgWxqztrNooG92RXvxSTWv"
   */
  their_did?: string;
  /**
   * Their label for connection
   * @example "Bob"
   */
  their_label?: string;
  /**
   * Other agent's public DID for connection
   * @example "2cpBmR3FqGKWi5EyUbpRY8"
   */
  their_public_did?: string;
  /**
   * Their role in the connection protocol
   * @example "requester"
   */
  their_role?: 'invitee' | 'requester' | 'inviter' | 'responder';
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface ConnectionInvitation {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /**
   * DID for connection invitation
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$|^did:([a-zA-Z0-9_]+)(:[a-zA-Z0-9_.%-]+)?:([a-zA-Z0-9_.%-]+(:[a-zA-Z0-9_.%-]+)*)((;[a-zA-Z0-9_.:%-]+=[a-zA-Z0-9_.:%-]*)*)(\/[^#?]*)?([?][^#]*)?(\#.*)?$$
   * @example "did:peer:WgWxqztrNooG92RXvxSTWv"
   */
  did?: string;
  /**
   * Optional image URL for connection invitation
   * @format url
   * @example "http://192.168.56.101/img/logo.jpg"
   */
  imageUrl?: string | null;
  /**
   * Optional label for connection invitation
   * @example "Bob"
   */
  label?: string;
  /** List of recipient keys */
  recipientKeys?: string[];
  /** List of routing keys */
  routingKeys?: string[];
  /**
   * Service endpoint at which to reach this agent
   * @example "http://192.168.56.101:8020"
   */
  serviceEndpoint?: string;
}

export interface ConnectionList {
  /** List of connection records */
  results: ConnRecord[];
}

export interface ConnectionListV1 {
  /** List of connection records */
  results: MaybeStoredConnectionsRecord[];
}

export interface ConnectionMetadata {
  /** Dictionary of metadata associated with connection. */
  results?: Record<string, any>;
}

export interface ConnectionMetadataSetRequest {
  /** Dictionary of metadata to set for connection. */
  metadata: Record<string, any>;
}

export interface ConnectionMetadataSetRequestV1 {
  /** Dictionary of metadata to set for connection. */
  metadata: Record<string, any>;
}

export interface ConnectionMetadataV1 {
  /** Dictionary of metadata associated with connection. */
  results?: Record<string, any>;
}

export type ConnectionModuleResponse = object;

export type ConnectionModuleResponseV1 = object;

export interface ConnectionStaticRequest {
  /** Alias to assign to this connection */
  alias?: string;
  /**
   * Local DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  my_did?: string;
  /** Seed to use for the local DID */
  my_seed?: string;
  /**
   * Remote DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  their_did?: string;
  /**
   * URL endpoint for other party
   * @pattern ^[A-Za-z0-9\.\-\+]+://([A-Za-z0-9][.A-Za-z0-9-_]+[A-Za-z0-9])+(:[1-9][0-9]*)?(/[^?&#]+)?$
   * @example "https://myhost:8021"
   */
  their_endpoint?: string;
  /** Other party's label for this connection */
  their_label?: string;
  /** Seed to use for the remote DID */
  their_seed?: string;
  /** Remote verification key */
  their_verkey?: string;
}

export interface ConnectionStaticRequestV1 {
  /** Alias to assign to this connection */
  alias?: string;
  /**
   * Local DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  my_did?: string;
  /** Seed to use for the local DID */
  my_seed?: string;
  /**
   * Remote DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  their_did?: string;
  /**
   * URL endpoint for other party
   * @pattern ^[A-Za-z0-9\.\-\+]+://([A-Za-z0-9][.A-Za-z0-9-_]+[A-Za-z0-9])+(:[1-9][0-9]*)?(/[^?&#]+)?$
   * @example "https://myhost:8021"
   */
  their_endpoint?: string;
  /** Other party's label for this connection */
  their_label?: string;
  /** Seed to use for the remote DID */
  their_seed?: string;
  /** Remote verification key */
  their_verkey?: string;
}

export interface ConnectionStaticResult {
  /**
   * Local DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  my_did: string;
  /**
   * My URL endpoint
   * @pattern ^[A-Za-z0-9\.\-\+]+://([A-Za-z0-9][.A-Za-z0-9-_]+[A-Za-z0-9])+(:[1-9][0-9]*)?(/[^?&#]+)?$
   * @example "https://myhost:8021"
   */
  my_endpoint: string;
  /**
   * My verification key
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44}$
   * @example "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
   */
  my_verkey: string;
  record: ConnRecord;
  /**
   * Remote DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  their_did: string;
  /**
   * Remote verification key
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44}$
   * @example "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
   */
  their_verkey: string;
}

export interface ConnectionStaticResultV1 {
  /**
   * Local DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  my_did: string;
  /**
   * My URL endpoint
   * @pattern ^[A-Za-z0-9\.\-\+]+://([A-Za-z0-9][.A-Za-z0-9-_]+[A-Za-z0-9])+(:[1-9][0-9]*)?(/[^?&#]+)?$
   * @example "https://myhost:8021"
   */
  my_endpoint: string;
  /**
   * My verification key
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44}$
   * @example "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
   */
  my_verkey: string;
  record: MaybeStoredConnectionsRecord;
  /**
   * Remote DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  their_did: string;
  /**
   * Remote verification key
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44}$
   * @example "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
   */
  their_verkey: string;
}

export interface Constraints {
  fields?: DIFField[];
  is_holder?: DIFHolder[];
  /** LimitDisclosure */
  limit_disclosure?: string;
  status_active?: 'required' | 'allowed' | 'disallowed';
  status_revoked?: 'required' | 'allowed' | 'disallowed';
  status_suspended?: 'required' | 'allowed' | 'disallowed';
  /** SubjectIsIssuer */
  subject_is_issuer?: 'required' | 'preferred';
}

export interface CreateDidIndyRequest {
  /**
   * Additional features to enable for the did.
   * @example "{}"
   */
  features?: Record<string, any>;
  /**
   * Additional configuration options. Supported options: did, seed, key_type. Default key_type is ed25519.
   * @example {"did":"did:indy:WRfXPg8dantKVubE3HX8pw","key_type":"ed25519","seed":"000000000000000000000000Trustee1"}
   */
  options?: Record<string, any>;
}

export interface CreateDidIndyResponse {
  /**
   * DID created
   * @example "did:indy:DFZgMggBEXcZFVQ2ZBTwdr"
   */
  did?: string;
  /**
   * Verification key
   * @example "BnSWTUQmdYCewSGFrRUhT6LmKdcCcSzRGqWXMPnEP168"
   */
  verkey?: string;
}

export interface CreateInvitationRequest {
  /**
   * Identifier for active mediation record to be used
   * @pattern [a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  mediation_id?: string;
  /** Optional metadata to attach to the connection created with the invitation */
  metadata?: Record<string, any>;
  /**
   * Optional label for connection invitation
   * @example "Bob"
   */
  my_label?: string;
  /** List of recipient keys */
  recipient_keys?: string[];
  /** List of routing keys */
  routing_keys?: string[];
  /**
   * Connection endpoint
   * @example "http://192.168.56.102:8020"
   */
  service_endpoint?: string;
}

export interface CreateKeyRequest {
  /**
   * Which key algorithm to use.
   * @example "ed25519"
   */
  alg?: string;
  /**
   * Optional kid to bind to the keypair, such as a verificationMethod.
   * @example "did:web:example.com#key-01"
   */
  kid?: string;
  /**
   * Optional seed to generate the key pair. Must enable insecure wallet mode.
   * @example "00000000000000000000000000000000"
   */
  seed?: string;
}

export interface CreateKeyResponse {
  /**
   * The associated kid
   * @example "did:web:example.com#key-01"
   */
  kid?: string;
  /**
   * The Public Key Multibase format (multikey)
   * @example "z6MkgKA7yrw5kYSiDuQFcye4bMaJpcfHFry3Bx45pdWh3s8i"
   */
  multikey?: string;
}

export interface CreateOptions {
  /**
   * Identifier for the DID. Must be unique within the namespace. If not provided, a random one will be generated.
   * @example "1"
   */
  identifier?: string;
  /**
   * Namespace for the DID
   * @example "prod"
   */
  namespace: string;
  /**
   * Portable flag
   * @example false
   */
  portable?: boolean;
  /**
   * Prerotation flag
   * @example false
   */
  prerotation?: boolean;
  /**
   * List of watchers for this DID.
   * @example ["https://watcher.webvh.test-suite.app"]
   */
  watchers?: string[];
  /**
   * The witness treshold
   * @example 1
   */
  witnessTreshold?: number;
}

export interface CreateWalletResponse {
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /** Mode regarding management of wallet key */
  key_management_mode: 'managed' | 'unmanaged';
  /** Settings for this wallet. */
  settings?: Record<string, any>;
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Authorization token to authenticate wallet requests
   * @example "eyJhbGciOiJFZERTQSJ9.eyJhIjogIjAifQ.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
   */
  token?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
  /**
   * Wallet record ID
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  wallet_id: string;
}

export interface CreateWalletTokenRequest {
  /**
   * Master key used for key derivation. Only required for unmanaged wallets.
   * @example "MySecretKey123"
   */
  wallet_key?: string;
}

export interface CreateWalletTokenResponse {
  /**
   * Authorization token to authenticate wallet requests
   * @example "eyJhbGciOiJFZERTQSJ9.eyJhIjogIjAifQ.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
   */
  token?: string;
}

export interface CredAttrSpec {
  /**
   * MIME type: omit for (null) default
   * @example "image/jpeg"
   */
  'mime-type'?: string | null;
  /**
   * Attribute name
   * @example "favourite_drink"
   */
  name: string;
  /**
   * Attribute value: base64-encode if MIME type is present
   * @example "martini"
   */
  value: string;
}

export interface CredDef {
  /**
   * Issuer Identifier of the credential definition or schema
   * @example "did:(method):WgWxqztrNooG92RXvxSTWv"
   */
  issuerId?: string;
  /**
   * Schema identifier
   * @example "did:(method):2:schema_name:1.0"
   */
  schemaId?: string;
  /**
   * The tag value passed in by the Issuer to an AnonCred's Credential Definition create and store implementation.
   * @example "default"
   */
  tag?: string;
  type?: 'CL';
  value?: CredDefValueSchemaAnonCreds;
}

export interface CredDefPostOptions {
  /**
   * Create transaction for endorser (optional, default false). Use this for agents who don't specify an author role but want to create a transaction for an endorser to sign.
   * @example false
   */
  create_transaction_for_endorser?: boolean;
  /**
   * Connection identifier (optional) (this is an example). You can set this if you know the endorser's connection id you want to use. If not specified then the agent will attempt to find an endorser connection.
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  endorser_connection_id?: string;
  /**
   * Maximum number of credential revocations per registry
   * @example 1000
   */
  revocation_registry_size?: number;
  /** Support credential revocation */
  support_revocation?: boolean;
}

export interface CredDefPostRequest {
  credential_definition?: InnerCredDef;
  options?: CredDefPostOptions;
}

export interface CredDefResult {
  credential_definition_metadata?: Record<string, any>;
  credential_definition_state?: CredDefState;
  job_id?: string;
  registration_metadata?: Record<string, any>;
}

export interface CredDefState {
  /** credential definition */
  credential_definition?: CredDef;
  /**
   * credential definition id
   * @example "did:(method):3:CL:20:tag"
   */
  credential_definition_id?: string | null;
  state?: 'finished' | 'failed' | 'action' | 'wait';
}

export interface CredDefStorageList {
  /** List of cred def storage records */
  results?: CredDefStorageRecord[];
}

export interface CredDefStorageOperationResponse {
  /** True if operation successful, false if otherwise */
  success: boolean;
}

export interface CredDefStorageRecord {
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Cred Def identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id: string;
  /**
   * Revocation registry size
   * @min 4
   * @max 32768
   * @example 1000
   */
  rev_reg_size?: number | null;
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id?: string;
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /** Revocation supported flag */
  support_revocation?: boolean;
  /**
   * Credential definition identifier tag
   * @default "default"
   * @example "default"
   */
  tag?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface CredDefValue {
  /** Primary value for credential definition */
  primary?: CredDefValuePrimary;
  /** Revocation value for credential definition */
  revocation?: CredDefValueRevocation;
}

export interface CredDefValuePrimary {
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  n?: string;
  r?: Generated;
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  rctxt?: string;
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  s?: string;
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  z?: string;
}

export interface CredDefValuePrimarySchemaAnonCreds {
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  n?: string;
  r?: Record<string, any>;
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  rctxt?: string;
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  s?: string;
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  z?: string;
}

export interface CredDefValueRevocation {
  /** @example "1 1F14F&ECB578F 2 095E45DDF417D" */
  g?: string;
  /** @example "1 1D64716fCDC00C 1 0C781960FA66E3D3 2 095E45DDF417D" */
  g_dash?: string;
  /** @example "1 16675DAE54BFAE8 2 095E45DD417D" */
  h?: string;
  /** @example "1 21E5EF9476EAF18 2 095E45DDF417D" */
  h0?: string;
  /** @example "1 236D1D99236090 2 095E45DDF417D" */
  h1?: string;
  /** @example "1 1C3AE8D1F1E277 2 095E45DDF417D" */
  h2?: string;
  /** @example "1 1B2A32CF3167 1 2490FEBF6EE55 1 0000000000000000" */
  h_cap?: string;
  /** @example "1 1D8549E8C0F8 2 095E45DDF417D" */
  htilde?: string;
  /** @example "1 142CD5E5A7DC 1 153885BD903312 2 095E45DDF417D" */
  pk?: string;
  /** @example "1 0C430AAB2B4710 1 1CB3A0932EE7E 1 0000000000000000" */
  u?: string;
  /** @example "1 153558BD903312 2 095E45DDF417D 1 0000000000000000" */
  y?: string;
}

export interface CredDefValueRevocationSchemaAnonCreds {
  /** @example "1 1F14F&ECB578F 2 095E45DDF417D" */
  g?: string;
  /** @example "1 1D64716fCDC00C 1 0C781960FA66E3D3 2 095E45DDF417D" */
  g_dash?: string;
  /** @example "1 16675DAE54BFAE8 2 095E45DD417D" */
  h?: string;
  /** @example "1 21E5EF9476EAF18 2 095E45DDF417D" */
  h0?: string;
  /** @example "1 236D1D99236090 2 095E45DDF417D" */
  h1?: string;
  /** @example "1 1C3AE8D1F1E277 2 095E45DDF417D" */
  h2?: string;
  /** @example "1 1B2A32CF3167 1 2490FEBF6EE55 1 0000000000000000" */
  h_cap?: string;
  /** @example "1 1D8549E8C0F8 2 095E45DDF417D" */
  htilde?: string;
  /** @example "1 142CD5E5A7DC 1 153885BD903312 2 095E45DDF417D" */
  pk?: string;
  /** @example "1 0C430AAB2B4710 1 1CB3A0932EE7E 1 0000000000000000" */
  u?: string;
  /** @example "1 153558BD903312 2 095E45DDF417D 1 0000000000000000" */
  y?: string;
}

export interface CredDefValueSchemaAnonCreds {
  /** Primary value for credential definition */
  primary?: CredDefValuePrimarySchemaAnonCreds;
  /** Revocation value for credential definition */
  revocation?: CredDefValueRevocationSchemaAnonCreds;
}

export interface CredInfoList {
  results?: IndyCredInfo[];
}

export interface CredRevIndyRecordsResult {
  /** Indy revocation registry delta */
  rev_reg_delta?: Record<string, any>;
}

export interface CredRevIndyRecordsResultSchemaAnonCreds {
  /** Indy revocation registry delta */
  rev_reg_delta?: Record<string, any>;
}

export interface CredRevRecordDetailsResult {
  results?: IssuerCredRevRecord[];
}

export interface CredRevRecordDetailsResultSchemaAnonCreds {
  results?: IssuerCredRevRecordSchemaAnonCreds[];
}

export interface CredRevRecordResult {
  result?: IssuerCredRevRecord;
}

export interface CredRevRecordResultSchemaAnonCreds {
  result?: IssuerCredRevRecordSchemaAnonCreds;
}

export interface CredRevokedResult {
  /** Whether credential is revoked on the ledger */
  revoked?: boolean;
}

export interface Credential {
  /**
   * The JSON-LD context of the credential
   * @example ["https://www.w3.org/2018/credentials/v1","https://www.w3.org/2018/credentials/examples/v1"]
   */
  '@context': any[];
  /** @example {"id":"https://example.com/credentials/status/3#94567","statusListCredential":"https://example.com/credentials/status/3","statusListIndex":"94567","statusPurpose":"revocation","type":"BitstringStatusListEntry"} */
  credentialStatus?: any;
  /** @example {"alumniOf":{"id":"did:example:c276e12ec21ebfeb1f712ebc6f1"},"id":"did:example:ebfeb1f712ebc6f1c276e12ec21"} */
  credentialSubject: any;
  /**
   * The expiration date
   * @pattern ^([0-9]{4})-([0-9]{2})-([0-9]{2})([Tt ]([0-9]{2}):([0-9]{2}):([0-9]{2})(\.[0-9]+)?)?(([Zz]|([+-])([0-9]{2}):([0-9]{2})))?$
   * @example "2010-01-01T19:23:24Z"
   */
  expirationDate?: string;
  /**
   * The ID of the credential
   * @pattern \w+:(\/?\/?)[^\s]+
   * @example "http://example.edu/credentials/1872"
   */
  id?: string;
  /**
   * The issuance date
   * @pattern ^([0-9]{4})-([0-9]{2})-([0-9]{2})([Tt ]([0-9]{2}):([0-9]{2}):([0-9]{2})(\.[0-9]+)?)?(([Zz]|([+-])([0-9]{2}):([0-9]{2})))?$
   * @example "2010-01-01T19:23:24Z"
   */
  issuanceDate?: string;
  /**
   * The JSON-LD Verifiable Credential Issuer. Either string of object with id field.
   * @example "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
   */
  issuer: any;
  /**
   * The proof of the credential
   * @example {"created":"2019-12-11T03:50:55","jws":"eyJhbGciOiAiRWREU0EiLCAiYjY0IjogZmFsc2UsICJjcml0JiNjQiXX0..lKJU0Df_keblRKhZAS9Qq6zybm-HqUXNVZ8vgEPNTAjQKBhQDxvXNo7nvtUBb_Eq1Ch6YBKY5qBQ","proofPurpose":"assertionMethod","type":"Ed25519Signature2018","verificationMethod":"did:key:z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL#z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL"}
   */
  proof?: LinkedDataProof;
  /**
   * The JSON-LD type of the credential
   * @example ["VerifiableCredential","AlumniCredential"]
   */
  type: string[];
  /**
   * The valid from date
   * @pattern ^([0-9]{4})-([0-9]{2})-([0-9]{2})([Tt ]([0-9]{2}):([0-9]{2}):([0-9]{2})(\.[0-9]+)?)?(([Zz]|([+-])([0-9]{2}):([0-9]{2})))?$
   * @example "2010-01-01T19:23:24Z"
   */
  validFrom?: string;
  /**
   * The valid until date
   * @pattern ^([0-9]{4})-([0-9]{2})-([0-9]{2})([Tt ]([0-9]{2}):([0-9]{2}):([0-9]{2})(\.[0-9]+)?)?(([Zz]|([+-])([0-9]{2}):([0-9]{2})))?$
   * @example "2010-01-01T19:23:24Z"
   */
  validUntil?: string;
  [key: string]: any;
}

export interface CredentialDefinition {
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  id?: string;
  /**
   * Schema identifier within credential definition identifier
   * @example "20"
   */
  schemaId?: string;
  /**
   * Tag within credential definition identifier
   * @example "tag"
   */
  tag?: string;
  /**
   * Signature type: CL for Camenisch-Lysyanskaya
   * @default "CL"
   * @example "CL"
   */
  type?: any;
  /** Credential definition primary and revocation values */
  value?: CredDefValue;
  /**
   * Node protocol version
   * @pattern ^[0-9.]+$
   * @example "1.0"
   */
  ver?: string;
}

export interface CredentialDefinitionGetResult {
  credential_definition?: CredentialDefinition;
}

export interface CredentialDefinitionSendRequest {
  /**
   * Revocation registry size
   * @min 4
   * @max 32768
   * @example 1000
   */
  revocation_registry_size?: number;
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id?: string;
  /** Revocation supported flag */
  support_revocation?: boolean;
  /**
   * Credential definition identifier tag
   * @example "default"
   */
  tag?: string;
}

export interface CredentialDefinitionSendResult {
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  credential_definition_id: string;
}

export interface CredentialDefinitionsCreatedResult {
  credential_definition_ids?: string[];
}

export interface CredentialOffer {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /** Human-readable comment */
  comment?: string | null;
  credential_preview?: CredentialPreview;
  'offers~attach': AttachDecorator[];
}

export interface CredentialPreview {
  /**
   * Message type identifier
   * @example "issue-credential/1.0/credential-preview"
   */
  '@type'?: string;
  attributes: CredAttrSpec[];
}

export interface CredentialProposal {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /** Human-readable comment */
  comment?: string | null;
  /**
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id?: string;
  credential_proposal?: CredentialPreview;
  /**
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  issuer_did?: string;
  /**
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id?: string;
  /**
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  schema_issuer_did?: string;
  schema_name?: string;
  /**
   * @pattern ^[0-9.]+$
   * @example "1.0"
   */
  schema_version?: string;
}

export interface CredentialStatusOptions {
  /**
   * Credential status method type to use for the credential. Should match status method registered in the Verifiable Credential Extension Registry
   * @example "CredentialStatusList2017"
   */
  type: string;
  [key: string]: any;
}

export interface CustomCreateWalletTokenRequest {
  /**
   * API key for this wallet
   * @example "3bd14a1e8fb645ddadf9913c0922ff3b"
   */
  api_key?: string;
  /**
   * Master key used for key derivation. Only required for unmanaged wallets.
   * @example "MySecretKey123"
   */
  wallet_key?: string;
}

export interface CustomUpdateWalletRequest {
  /** Agent config key-value pairs */
  extra_settings?: Record<string, any>;
  /**
   * Image url for this wallet. This image url is publicized            (self-attested) to other agents as part of forming a connection.
   * @example "https://aries.ca/images/sample.png"
   */
  image_url?: string;
  /**
   * Label for this wallet. This label is publicized (self-attested) to other agents as part of forming a connection.
   * @example "Alice"
   */
  label?: string;
  /**
   * Webhook target dispatch type for this wallet. default: Dispatch only to webhooks associated with this wallet. base: Dispatch only to webhooks associated with the base wallet. both: Dispatch to both webhook targets.
   * @example "default"
   */
  wallet_dispatch_type?: 'default' | 'both' | 'base';
  /** List of Webhook URLs associated with this subwallet */
  wallet_webhook_urls?: string[];
}

export interface DID {
  /**
   * DID of interest
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$|^did:([a-zA-Z0-9_]+)(:[a-zA-Z0-9_.%-]+)?:([a-zA-Z0-9_.%-]+(:[a-zA-Z0-9_.%-]+)*)((;[a-zA-Z0-9_.:%-]+=[a-zA-Z0-9_.:%-]*)*)(\/[^#?]*)?([?][^#]*)?(\#.*)?$$
   * @example "did:peer:WgWxqztrNooG92RXvxSTWv"
   */
  did: string;
  /**
   * Key type associated with the DID
   * @example "ed25519"
   */
  key_type: 'ed25519' | 'bls12381g2' | 'p256';
  /** Additional metadata associated with the DID */
  metadata?: Record<string, any>;
  /**
   * Did method associated with the DID
   * @example "sov"
   */
  method: string;
  /**
   * Whether DID is current public DID, posted to ledger but not current public DID, or local to the wallet
   * @example "wallet_only"
   */
  posture: 'public' | 'posted' | 'wallet_only';
  /**
   * Public verification key
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44}$
   * @example "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
   */
  verkey: string;
}

export interface DIDCreate {
  /**
   * Method for the requested DID.Supported methods are 'key', 'sov', and any other registered method.
   * @example "sov"
   */
  method?: string;
  /** To define a key type and/or a did depending on chosen DID method. */
  options?: DIDCreateOptions;
  /**
   * Optional seed to use for DID, Must be enabled in configuration before use.
   * @example "000000000000000000000000Trustee1"
   */
  seed?: string;
}

export interface DIDCreateOptions {
  /**
   * Specify final value of the did (including did:<method>: prefix)if the method supports or requires so.
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$|^did:([a-zA-Z0-9_]+)(:[a-zA-Z0-9_.%-]+)?:([a-zA-Z0-9_.%-]+(:[a-zA-Z0-9_.%-]+)*)((;[a-zA-Z0-9_.:%-]+=[a-zA-Z0-9_.:%-]*)*)(\/[^#?]*)?([?][^#]*)?(\#.*)?$$
   * @example "did:peer:WgWxqztrNooG92RXvxSTWv"
   */
  did?: string;
  /**
   * Key type to use for the DID keypair. Validated with the chosen DID method's supported key types.
   * @example "ed25519"
   */
  key_type: 'ed25519' | 'bls12381g2' | 'p256';
}

export interface DIDEndpoint {
  /**
   * DID of interest
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  did: string;
  /**
   * Endpoint to set (omit to delete)
   * @pattern ^[A-Za-z0-9\.\-\+]+://([A-Za-z0-9][.A-Za-z0-9-_]+[A-Za-z0-9])+(:[1-9][0-9]*)?(/[^?&#]+)?$
   * @example "https://myhost:8021"
   */
  endpoint?: string;
}

export interface DIDEndpointWithType {
  /**
   * DID of interest
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  did: string;
  /**
   * Endpoint to set (omit to delete)
   * @pattern ^[A-Za-z0-9\.\-\+]+://([A-Za-z0-9][.A-Za-z0-9-_]+[A-Za-z0-9])+(:[1-9][0-9]*)?(/[^?&#]+)?$
   * @example "https://myhost:8021"
   */
  endpoint?: string;
  /**
   * Endpoint type to set (default 'Endpoint'); affects only public or posted DIDs
   * @example "Endpoint"
   */
  endpoint_type?: 'Endpoint' | 'Profile' | 'LinkedDomains';
  /**
   * Mediation ID to use for endpoint information.
   * @pattern [a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  mediation_id?: string;
}

export interface DIDList {
  /** DID list */
  results?: DID[];
}

export interface DIDResult {
  result?: DID;
}

export interface DIDRotateRequestJSON {
  /**
   * The DID the rotating party is rotating to
   * @example "did:web:example.com"
   */
  to_did: string;
}

export interface DIDXRejectRequest {
  /**
   * Reason for rejecting the DID Exchange
   * @example "Request rejected"
   */
  reason?: string;
}

export interface DIDXRequest {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /**
   * DID of exchange
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$|^did:([a-zA-Z0-9_]+)(:[a-zA-Z0-9_.%-]+)?:([a-zA-Z0-9_.%-]+(:[a-zA-Z0-9_.%-]+)*)((;[a-zA-Z0-9_.:%-]+=[a-zA-Z0-9_.:%-]*)*)(\/[^#?]*)?([?][^#]*)?(\#.*)?$$
   * @example "did:peer:WgWxqztrNooG92RXvxSTWv"
   */
  did?: string;
  /** As signed attachment, DID Doc associated with DID */
  'did_doc~attach'?: AttachDecorator;
  /**
   * A self-attested string that the receiver may want to display to the user about the context-specific goal of the out-of-band message
   * @example "To issue a Faber College Graduate credential"
   */
  goal?: string;
  /**
   * A self-attested code the receiver may want to display to the user or use in automatically deciding what to do with the out-of-band message
   * @example "issue-vc"
   */
  goal_code?: string;
  /**
   * Label for DID exchange request
   * @example "Request to connect with Bob"
   */
  label: string;
}

export interface DIFField {
  filter?: Filter;
  /** ID */
  id?: string;
  path?: string[];
  /** Preference */
  predicate?: 'required' | 'preferred';
  /** Purpose */
  purpose?: string;
}

export interface DIFHolder {
  /** Preference */
  directive?: 'required' | 'preferred';
  field_id?: string[];
}

export interface DIFOptions {
  /**
   * Challenge protect against replay attack
   * @pattern [a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  challenge?: string;
  /**
   * Domain protect against replay attack
   * @example "4jt78h47fh47"
   */
  domain?: string;
}

export interface DIFPresSpec {
  /** Issuer identifier to sign the presentation, if different from current public DID */
  issuer_id?: string;
  presentation_definition?: PresentationDefinition;
  /**
   * Mapping of input_descriptor id to list of stored W3C credential record_id
   * @example {"<input descriptor id_1>":["<record id_1>","<record id_2>"],"<input descriptor id_2>":["<record id>"]}
   */
  record_ids?: Record<string, any>;
  /**
   * reveal doc [JSON-LD frame] dict used to derive the credential when selective disclosure is required
   * @example {"@context":["https://www.w3.org/2018/credentials/v1","https://w3id.org/security/bbs/v1"],"@explicit":true,"@requireAll":true,"credentialSubject":{"@explicit":true,"@requireAll":true,"Observation":[{"effectiveDateTime":{},"@explicit":true,"@requireAll":true}]},"issuanceDate":{},"issuer":{},"type":["VerifiableCredential","LabReport"]}
   */
  reveal_doc?: Record<string, any>;
}

export interface DIFProofProposal {
  input_descriptors?: InputDescriptors[];
  options?: DIFOptions;
}

export interface DIFProofRequest {
  options?: DIFOptions;
  presentation_definition: PresentationDefinition;
  [key: string]: any;
}

export interface DRPCRecord {
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * RPC request
   * @example {"id":1,"jsonrpc":"2.0","method":"example.method","params":["1","a"]}
   */
  request: any;
  /**
   * RPC response
   * @default null
   * @example {"id":1,"jsonrpc":"2.0","result":"result"}
   */
  response?: any;
  /**
   * RPC state
   * @example "request-received"
   */
  state: 'request-sent' | 'request-received' | 'completed';
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface DRPCRecordList {
  /** List of DIDComm RPC request/reponse exchanges */
  results: DRPCRecord[];
}

export interface DRPCRequestJSON {
  /**
   * RPC Request
   * @example {"id":1,"jsonrpc":"2.0","method":"example.method","params":["1","a"]}
   */
  request: any;
}

export interface DRPCRequestMessage {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /**
   * RPC request
   * @example {"id":1,"jsonrpc":"2.0","method":"example.method","params":["1","a"]}
   */
  request: any;
}

export interface DRPCResponseJSON {
  /**
   * RPC Response
   * @example {"id":1,"jsonrpc":"2.0","result":"result"}
   */
  response: any;
  /**
   * Thread identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  thread_id: string;
}

export interface DRPCResponseMessage {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /**
   * RPC response
   * @example {"id":1,"jsonrpc":"2.0","result":"result"}
   */
  response: any;
}

export interface DataIntegrityProofOptions {
  /**
   * The value is used once for a particular domain and window of time. This value is used to mitigate replay attacks.
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  challenge?: string;
  /**
   * The date and time the proof was created is OPTIONAL and, if included, MUST be specified as an [XMLSCHEMA11-2] dateTimeStamp string
   * @example "2010-01-01T19:23:24Z"
   */
  created?: string;
  /**
   * An identifier for the cryptographic suite that can be used to verify the proof.
   * @example "eddsa-jcs-2022"
   */
  cryptosuite: string;
  /**
   * It conveys one or more security domains in which the proof is meant to be used.
   * @example "example.com"
   */
  domain?: string;
  /**
   * The expires property is OPTIONAL and, if present, specifies when the proof expires. If present, it MUST be an [XMLSCHEMA11-2] dateTimeStamp string
   * @example "2010-01-01T19:23:24Z"
   */
  expires?: string;
  /**
   * An optional identifier for the proof, which MUST be a URL [URL], such as a UUID as a URN
   * @example "urn:uuid:6a1676b8-b51f-11ed-937b-d76685a20ff5"
   */
  id?: string;
  /**
   * One use of this field is to increase privacy by decreasing linkability that is the result of deterministically generated signatures.
   * @example "CF69iO3nfvqRsRBNElE8b4wO39SyJHPM7Gg1nExltW5vSfQA1lvDCR/zXX1To0/4NLo=="
   */
  nonce?: string;
  /**
   * Each value identifies another data integrity proof that MUST verify before the current proof is processed.
   * @example "urn:uuid:6a1676b8-b51f-11ed-937b-d76685a20ff5"
   */
  previousProof?: string;
  /**
   * The proof purpose acts as a safeguard to prevent the proof from being misused by being applied to a purpose other than the one that was intended.
   * @example "assertionMethod"
   */
  proofPurpose: string;
  /**
   * The value of the proof signature.
   * @example "zsy1AahqbzJQ63n9RtekmwzqZeVj494VppdAVJBnMYrTwft6cLJJGeTSSxCCJ6HKnRtwE7jjDh6sB2z2AAiZY9BBnCD8wUVgwqH3qchGRCuC2RugA4eQ9fUrR4Yuycac3caiaaay"
   */
  proofValue?: string;
  /**
   * The specific type of proof MUST be specified as a string that maps to a URL [URL].
   * @example "DataIntegrityProof"
   */
  type: string;
  /**
   * A verification method is the means and information needed to verify the proof.
   * @pattern \w+:(\/?\/?)[^\s]+
   * @example "did:key:z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL#z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL"
   */
  verificationMethod: string;
  [key: string]: any;
}

export interface Date {
  /**
   * Expiry Date
   * @format date-time
   * @example "2021-03-29T05:22:19Z"
   */
  expires_time: string;
}

export interface DefaultConfigValues {
  /** Endorser config */
  connected_to_endorsers?: EndorserLedgerConfig[];
  /** Public DID config */
  created_public_did?: string[];
}

export type DeleteResponse = object;

export interface Disclose {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /** List of protocol descriptors */
  protocols: ProtocolDescriptor[];
}

export interface Disclosures {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /** List of protocol or goal_code descriptors */
  disclosures: any[];
}

export interface Doc {
  /** Credential to sign */
  credential: Record<string, any>;
  /** Signature options */
  options: SignatureOptions;
}

export interface DocumentVerificationResult {
  document?: Record<string, any>;
  errors?: string[];
  results?: ProofResult[];
  verified: boolean;
}

export interface EndorserInfo {
  /** Endorser DID */
  endorser_did: string;
  /** Endorser Name */
  endorser_name?: string;
}

export interface EndorserLedgerConfig {
  /** Endorser alias/identifier */
  endorser_alias: string;
  /** Ledger identifier */
  ledger_id: string;
}

export interface EndpointsResult {
  /**
   * My endpoint
   * @pattern ^[A-Za-z0-9\.\-\+]+://([A-Za-z0-9][.A-Za-z0-9-_]+[A-Za-z0-9])+(:[1-9][0-9]*)?(/[^?&#]+)?$
   * @example "https://myhost:8021"
   */
  my_endpoint?: string;
  /**
   * Their endpoint
   * @pattern ^[A-Za-z0-9\.\-\+]+://([A-Za-z0-9][.A-Za-z0-9-_]+[A-Za-z0-9])+(:[1-9][0-9]*)?(/[^?&#]+)?$
   * @example "https://myhost:8021"
   */
  their_endpoint?: string;
}

export interface EndpointsResultV1 {
  /**
   * My endpoint
   * @pattern ^[A-Za-z0-9\.\-\+]+://([A-Za-z0-9][.A-Za-z0-9-_]+[A-Za-z0-9])+(:[1-9][0-9]*)?(/[^?&#]+)?$
   * @example "https://myhost:8021"
   */
  my_endpoint?: string;
  /**
   * Their endpoint
   * @pattern ^[A-Za-z0-9\.\-\+]+://([A-Za-z0-9][.A-Za-z0-9-_]+[A-Za-z0-9])+(:[1-9][0-9]*)?(/[^?&#]+)?$
   * @example "https://myhost:8021"
   */
  their_endpoint?: string;
}

export interface FetchCredentialResponse {
  results?: VerifiableCredential;
}

export interface FetchKeyResponse {
  /**
   * The associated kid
   * @example "did:web:example.com#key-01"
   */
  kid?: string;
  /**
   * The Public Key Multibase format (multikey)
   * @example "z6MkgKA7yrw5kYSiDuQFcye4bMaJpcfHFry3Bx45pdWh3s8i"
   */
  multikey?: string;
}

export interface Filter {
  /** Const */
  const?: any;
  enum?: any[];
  /** ExclusiveMaximum */
  exclusiveMaximum?: any;
  /** ExclusiveMinimum */
  exclusiveMinimum?: any;
  /** Format */
  format?: string;
  /**
   * Max Length
   * @example 1234
   */
  maxLength?: number;
  /** Maximum */
  maximum?: any;
  /**
   * Min Length
   * @example 1234
   */
  minLength?: number;
  /** Minimum */
  minimum?: any;
  /**
   * Not
   * @example false
   */
  not?: boolean;
  /** Pattern */
  pattern?: string;
  /** Type */
  type?: string;
}

export interface Generated {
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  master_secret?: string;
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  number?: string;
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  remainder?: string;
}

export interface GetCredDefResult {
  /** credential definition */
  credential_definition?: CredDef;
  /**
   * credential definition id
   * @example "did:(method):3:CL:20:tag"
   */
  credential_definition_id?: string;
  credential_definitions_metadata?: Record<string, any>;
  resolution_metadata?: Record<string, any>;
}

export interface GetCredDefsResponse {
  credential_definition_ids?: string[];
}

export interface GetDIDEndpointResponse {
  /**
   * Full verification key
   * @pattern ^[A-Za-z0-9\.\-\+]+://([A-Za-z0-9][.A-Za-z0-9-_]+[A-Za-z0-9])+(:[1-9][0-9]*)?(/[^?&#]+)?$
   * @example "https://myhost:8021"
   */
  endpoint?: string | null;
}

export interface GetDIDVerkeyResponse {
  /**
   * Full verification key
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44}$
   * @example "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
   */
  verkey?: string | null;
}

export interface GetNymRoleResponse {
  /**
   * Ledger role
   * @example "ENDORSER"
   */
  role?:
    | 'STEWARD'
    | 'TRUSTEE'
    | 'ENDORSER'
    | 'NETWORK_MONITOR'
    | 'USER'
    | 'ROLE_REMOVE';
}

export interface GetSchemaResult {
  resolution_metadata?: Record<string, any>;
  schema?: AnonCredsSchema;
  /**
   * Schema identifier
   * @example "did:(method):2:schema_name:1.0"
   */
  schema_id?: string;
  schema_metadata?: Record<string, any>;
}

export interface GetSchemasResponse {
  schema_ids?: string[];
}

export interface Hangup {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
}

export type HolderModuleResponse = object;

export interface IndyAttrValue {
  /**
   * Attribute encoded value
   * @pattern ^-?[0-9]*$
   * @example "-1"
   */
  encoded: string;
  /** Attribute raw value */
  raw: string;
}

export interface IndyCredAbstract {
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id: string;
  /** Key correctness proof */
  key_correctness_proof: IndyKeyCorrectnessProof;
  /**
   * Nonce in credential abstract
   * @pattern ^[0-9]*$
   * @example "0"
   */
  nonce: string;
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id: string;
}

export interface IndyCredInfo {
  /** Attribute names and value */
  attrs?: Record<string, string>;
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id?: string;
  /**
   * Credential revocation identifier
   * @pattern ^[1-9][0-9]*$
   * @example "12345"
   */
  cred_rev_id?: string | null;
  /**
   * Wallet referent
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  referent?: string;
  /**
   * Revocation registry identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)
   * @example "WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0"
   */
  rev_reg_id?: string | null;
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id?: string;
}

export interface IndyCredPrecis {
  /** Credential info */
  cred_info: IndyCredInfo;
  /** Non-revocation interval from presentation request */
  interval?: IndyNonRevocationInterval;
  presentation_referents?: string[];
}

export interface IndyCredRequest {
  /** Blinded master secret */
  blinded_ms: Record<string, any>;
  /** Blinded master secret correctness proof */
  blinded_ms_correctness_proof: Record<string, any>;
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id: string;
  /**
   * Nonce in credential request
   * @pattern ^[0-9]*$
   * @example "0"
   */
  nonce: string;
  /**
   * Prover DID/Random String/UUID
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  prover_did: string;
}

export interface IndyCredential {
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id: string;
  /** Revocation registry state */
  rev_reg?: Record<string, any>;
  /**
   * Revocation registry identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)
   * @example "WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0"
   */
  rev_reg_id?: string | null;
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id: string;
  /** Credential signature */
  signature: Record<string, any>;
  /** Credential signature correctness proof */
  signature_correctness_proof: Record<string, any>;
  /** Credential attributes */
  values: Record<string, IndyAttrValue>;
  /** Witness for revocation proof */
  witness?: Record<string, any>;
}

export interface IndyEQProof {
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  a_prime?: string;
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  e?: string;
  m?: Record<string, string>;
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  m2?: string;
  revealed_attrs?: Record<string, string>;
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  v?: string;
}

export interface IndyGEProof {
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  alpha?: string;
  /**
   * @pattern ^[0-9]*$
   * @example "0"
   */
  mj?: string;
  predicate?: IndyGEProofPred;
  r?: Record<string, string>;
  t?: Record<string, string>;
  u?: Record<string, string>;
}

export interface IndyGEProofPred {
  /** Attribute name, indy-canonicalized */
  attr_name?: string;
  /** Predicate type */
  p_type?: 'LT' | 'LE' | 'GE' | 'GT';
  /** Predicate threshold value */
  value?: number;
}

export interface IndyKeyCorrectnessProof {
  /**
   * c in key correctness proof
   * @pattern ^[0-9]*$
   * @example "0"
   */
  c: string;
  /** xr_cap in key correctness proof */
  xr_cap: string[][];
  /**
   * xz_cap in key correctness proof
   * @pattern ^[0-9]*$
   * @example "0"
   */
  xz_cap: string;
}

export interface IndyNonRevocProof {
  c_list?: Record<string, string>;
  x_list?: Record<string, string>;
}

export interface IndyNonRevocationInterval {
  /**
   * Earliest time of interest in non-revocation interval
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  from?: number;
  /**
   * Latest time of interest in non-revocation interval
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  to?: number;
}

export interface IndyPresAttrSpec {
  /**
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id?: string;
  /**
   * MIME type (default null)
   * @example "image/jpeg"
   */
  'mime-type'?: string;
  /**
   * Attribute name
   * @example "favourite_drink"
   */
  name: string;
  /**
   * Credential referent
   * @example "0"
   */
  referent?: string;
  /**
   * Attribute value
   * @example "martini"
   */
  value?: string;
}

export interface IndyPresPredSpec {
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id?: string;
  /**
   * Attribute name
   * @example "high_score"
   */
  name: string;
  /**
   * Predicate type ('<', '<=', '>=', or '>')
   * @example ">="
   */
  predicate: '<' | '<=' | '>=' | '>';
  /** Threshold value */
  threshold: number;
}

export interface IndyPresPreview {
  /**
   * Message type identifier
   * @example "https://didcomm.org/present-proof/1.0/presentation-preview"
   */
  '@type'?: string;
  attributes: IndyPresAttrSpec[];
  predicates: IndyPresPredSpec[];
}

export interface IndyPresSpec {
  /** Nested object mapping proof request attribute referents to requested-attribute specifiers */
  requested_attributes: Record<string, IndyRequestedCredsRequestedAttr>;
  /** Nested object mapping proof request predicate referents to requested-predicate specifiers */
  requested_predicates: Record<string, IndyRequestedCredsRequestedPred>;
  /** Self-attested attributes to build into proof */
  self_attested_attributes: Record<string, string>;
  /**
   * Whether to trace event (default false)
   * @example false
   */
  trace?: boolean;
}

export interface IndyPrimaryProof {
  /** Indy equality proof */
  eq_proof?: IndyEQProof | null;
  /** Indy GE proofs */
  ge_proofs?: IndyGEProof[] | null;
}

export interface IndyProof {
  /** Indy proof.identifiers content */
  identifiers?: IndyProofIdentifier[];
  /** Indy proof.proof content */
  proof?: IndyProofProof;
  /** Indy proof.requested_proof content */
  requested_proof?: IndyProofRequestedProof;
}

export interface IndyProofIdentifier {
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id?: string;
  /**
   * Revocation registry identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)
   * @example "WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0"
   */
  rev_reg_id?: string | null;
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id?: string;
  /**
   * Timestamp epoch
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  timestamp?: number | null;
}

export interface IndyProofProof {
  /** Indy proof aggregated proof */
  aggregated_proof?: IndyProofProofAggregatedProof;
  /** Indy proof proofs */
  proofs?: IndyProofProofProofsProof[];
}

export interface IndyProofProofAggregatedProof {
  /** c_hash value */
  c_hash?: string;
  /** c_list value */
  c_list?: number[][];
}

export interface IndyProofProofProofsProof {
  /** Indy non-revocation proof */
  non_revoc_proof?: IndyNonRevocProof | null;
  /** Indy primary proof */
  primary_proof?: IndyPrimaryProof;
}

export interface IndyProofReqAttrSpec {
  /**
   * Attribute name
   * @example "favouriteDrink"
   */
  name?: string;
  /** Attribute name group */
  names?: string[];
  non_revoked?: IndyProofReqAttrSpecNonRevoked | null;
  /** If present, credential must satisfy one of given restrictions: specify schema_id, schema_issuer_did, schema_name, schema_version, issuer_did, cred_def_id, and/or attr::<attribute-name>::value where <attribute-name> represents a credential attribute name */
  restrictions?: Record<string, string>[];
}

export interface IndyProofReqAttrSpecNonRevoked {
  /**
   * Earliest time of interest in non-revocation interval
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  from?: number;
  /**
   * Latest time of interest in non-revocation interval
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  to?: number;
}

export interface IndyProofReqPredSpec {
  /**
   * Attribute name
   * @example "index"
   */
  name: string;
  non_revoked?: IndyProofReqPredSpecNonRevoked | null;
  /**
   * Predicate type ('<', '<=', '>=', or '>')
   * @example ">="
   */
  p_type: '<' | '<=' | '>=' | '>';
  /** Threshold value */
  p_value: number;
  /** If present, credential must satisfy one of given restrictions: specify schema_id, schema_issuer_did, schema_name, schema_version, issuer_did, cred_def_id, and/or attr::<attribute-name>::value where <attribute-name> represents a credential attribute name */
  restrictions?: Record<string, string>[];
}

export interface IndyProofReqPredSpecNonRevoked {
  /**
   * Earliest time of interest in non-revocation interval
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  from?: number;
  /**
   * Latest time of interest in non-revocation interval
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  to?: number;
}

export interface IndyProofRequest {
  /**
   * Proof request name
   * @example "Proof request"
   */
  name?: string;
  non_revoked?: IndyProofRequestNonRevoked | null;
  /**
   * Nonce
   * @pattern ^[1-9][0-9]*$
   * @example "1"
   */
  nonce?: string;
  /** Requested attribute specifications of proof request */
  requested_attributes: Record<string, IndyProofReqAttrSpec>;
  /** Requested predicate specifications of proof request */
  requested_predicates: Record<string, IndyProofReqPredSpec>;
  /**
   * Proof request version
   * @pattern ^[0-9.]+$
   * @example "1.0"
   */
  version?: string;
}

export interface IndyProofRequestNonRevoked {
  /**
   * Earliest time of interest in non-revocation interval
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  from?: number;
  /**
   * Latest time of interest in non-revocation interval
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  to?: number;
}

export interface IndyProofRequestedProof {
  /** Proof requested proof predicates. */
  predicates?: Record<string, IndyProofRequestedProofPredicate>;
  /** Proof requested proof revealed attribute groups */
  revealed_attr_groups?: Record<
    string,
    IndyProofRequestedProofRevealedAttrGroup
  >;
  /** Proof requested proof revealed attributes */
  revealed_attrs?: Record<string, IndyProofRequestedProofRevealedAttr>;
  /** Proof requested proof self-attested attributes */
  self_attested_attrs?: Record<string, any>;
  /** Unrevealed attributes */
  unrevealed_attrs?: Record<string, any>;
}

export interface IndyProofRequestedProofPredicate {
  /** Sub-proof index */
  sub_proof_index?: number;
}

export interface IndyProofRequestedProofRevealedAttr {
  /**
   * Encoded value
   * @pattern ^-?[0-9]*$
   * @example "-1"
   */
  encoded?: string;
  /** Raw value */
  raw?: string;
  /** Sub-proof index */
  sub_proof_index?: number;
}

export interface IndyProofRequestedProofRevealedAttrGroup {
  /** Sub-proof index */
  sub_proof_index?: number;
  /** Indy proof requested proof revealed attr groups group value */
  values?: Record<string, RawEncoded>;
}

export interface IndyRequestedCredsRequestedAttr {
  /**
   * Wallet credential identifier (typically but not necessarily a UUID)
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_id: string;
  /** Whether to reveal attribute in proof (default true) */
  revealed?: boolean;
}

export interface IndyRequestedCredsRequestedPred {
  /**
   * Wallet credential identifier (typically but not necessarily a UUID)
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_id: string;
  /**
   * Epoch timestamp of interest for non-revocation proof
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  timestamp?: number;
}

export interface IndyRevRegDef {
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  credDefId?: string;
  /**
   * Indy revocation registry identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)
   * @example "WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0"
   */
  id?: string;
  /**
   * Revocation registry type (specify CL_ACCUM)
   * @example "CL_ACCUM"
   */
  revocDefType?: 'CL_ACCUM';
  /** Revocation registry tag */
  tag?: string;
  /** Revocation registry definition value */
  value?: IndyRevRegDefValue;
  /**
   * Version of revocation registry definition
   * @pattern ^[0-9.]+$
   * @example "1.0"
   */
  ver?: string;
}

export interface IndyRevRegDefValue {
  /** Issuance type */
  issuanceType?: 'ISSUANCE_ON_DEMAND' | 'ISSUANCE_BY_DEFAULT';
  /**
   * Maximum number of credentials; registry size
   * @min 1
   * @example 10
   */
  maxCredNum?: number;
  /** Public keys */
  publicKeys?: IndyRevRegDefValuePublicKeys;
  /**
   * Tails hash value
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44}$
   * @example "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
   */
  tailsHash?: string;
  /** Tails file location */
  tailsLocation?: string;
}

export interface IndyRevRegDefValuePublicKeys {
  accumKey?: IndyRevRegDefValuePublicKeysAccumKey;
}

export interface IndyRevRegDefValuePublicKeysAccumKey {
  /**
   * Value for z
   * @example "1 120F522F81E6B7 1 09F7A59005C4939854"
   */
  z?: string;
}

export interface IndyRevRegEntry {
  /** Revocation registry entry value */
  value?: IndyRevRegEntryValue;
  /**
   * Version of revocation registry entry
   * @pattern ^[0-9.]+$
   * @example "1.0"
   */
  ver?: string;
}

export interface IndyRevRegEntryValue {
  /**
   * Accumulator value
   * @example "21 11792B036AED0AAA12A4 4 298B2571FFC63A737"
   */
  accum?: string;
  /**
   * Previous accumulator value
   * @example "21 137AC810975E4 6 76F0384B6F23"
   */
  prevAccum?: string;
  /** Revoked credential revocation identifiers */
  revoked?: number[];
}

export interface InnerCredDef {
  /**
   * Issuer Identifier of the credential definition
   * @example "did:(method):WgWxqztrNooG92RXvxSTWv"
   */
  issuerId: string;
  /**
   * Schema identifier
   * @example "did:(method):2:schema_name:1.0"
   */
  schemaId: string;
  /**
   * Credential definition tag
   * @example "default"
   */
  tag: string;
}

export interface InnerRevRegDef {
  /**
   * Credential definition identifier
   * @example "did:(method):2:schema_name:1.0"
   */
  credDefId: string;
  /**
   * Issuer Identifier of the credential definition or schema
   * @example "did:(method):WgWxqztrNooG92RXvxSTWv"
   */
  issuerId: string;
  /**
   * Maximum number of credential revocations per registry
   * @example 777
   */
  maxCredNum: number;
  /**
   * tag for revocation registry
   * @example "default"
   */
  tag: string;
}

export interface InputDescriptors {
  constraints?: Constraints;
  group?: string[];
  /** ID */
  id?: string;
  /** Metadata dictionary */
  metadata?: Record<string, any>;
  /** Name */
  name?: string;
  /** Purpose */
  purpose?: string;
  /**
   * Accepts a list of schema or a dict containing filters like oneof_filter.
   * @example {"oneof_filter":[[{"uri":"https://www.w3.org/Test1#Test1"},{"uri":"https://www.w3.org/Test2#Test2"}],{"oneof_filter":[[{"uri":"https://www.w3.org/Test1#Test1"}],[{"uri":"https://www.w3.org/Test2#Test2"}]]}]}
   */
  schema?: SchemasInputDescriptorFilter;
}

export type IntroModuleResponse = object;

export interface InvitationCreateRequest {
  /**
   * List of mime type in order of preference that should be use in responding to the message
   * @example ["didcomm/aip1","didcomm/aip2;env=rfc19"]
   */
  accept?: string[];
  /**
   * Alias for connection
   * @example "Barry"
   */
  alias?: string;
  /** Optional invitation attachments */
  attachments?: AttachmentDef[];
  /**
   * A self-attested string that the receiver may want to display to the user about the context-specific goal of the out-of-band message
   * @example "To issue a Faber College Graduate credential"
   */
  goal?: string;
  /**
   * A self-attested code the receiver may want to display to the user or use in automatically deciding what to do with the out-of-band message
   * @example "issue-vc"
   */
  goal_code?: string;
  handshake_protocols?: string[];
  /**
   * Identifier for active mediation record to be used
   * @pattern [a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  mediation_id?: string;
  /** Optional metadata to attach to the connection created with the invitation */
  metadata?: Record<string, any>;
  /**
   * Label for connection invitation
   * @example "Invitation to Barry"
   */
  my_label?: string;
  /**
   * OOB protocol version
   * @example "1.1"
   */
  protocol_version?: string;
  /**
   * DID to use in invitation
   * @example "did:example:123"
   */
  use_did?: string;
  /**
   * DID method to use in invitation
   * @example "did:peer:2"
   */
  use_did_method?: 'did:peer:2' | 'did:peer:4';
  /**
   * Whether to use public DID in invitation
   * @example false
   */
  use_public_did?: boolean;
}

export interface InvitationMessage {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /**
   * List of mime type in order of preference
   * @example ["didcomm/aip1","didcomm/aip2;env=rfc19"]
   */
  accept?: string[];
  /**
   * A self-attested string that the receiver may want to display to the user about the context-specific goal of the out-of-band message
   * @example "To issue a Faber College Graduate credential"
   */
  goal?: string;
  /**
   * A self-attested code the receiver may want to display to the user or use in automatically deciding what to do with the out-of-band message
   * @example "issue-vc"
   */
  goal_code?: string;
  handshake_protocols?: string[];
  /**
   * Optional image URL for out-of-band invitation
   * @format url
   * @example "http://192.168.56.101/img/logo.jpg"
   */
  imageUrl?: string | null;
  /**
   * Optional label
   * @example "Bob"
   */
  label?: string;
  /** Optional request attachment */
  'requests~attach'?: AttachDecorator[];
  /** @example [{"did":"WgWxqztrNooG92RXvxSTWv","id":"string","recipientKeys":["did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"],"routingKeys":["did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"],"serviceEndpoint":"http://192.168.56.101:8020","type":"string"},"did:sov:WgWxqztrNooG92RXvxSTWv"] */
  services?: any[];
}

export interface InvitationRecord {
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Invitation message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  invi_msg_id?: string;
  /** Out of band invitation message */
  invitation?: InvitationMessage;
  /**
   * Invitation record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  invitation_id?: string;
  /**
   * Invitation message URL
   * @example "https://example.com/endpoint?c_i=eyJAdHlwZSI6ICIuLi4iLCAiLi4uIjogIi4uLiJ9XX0="
   */
  invitation_url?: string;
  /**
   * Out of band record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  oob_id?: string;
  /**
   * Out of band message exchange state
   * @example "await_response"
   */
  state?: string;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export type InvitationRecordResponse = object;

export interface InvitationResponse {
  /**
   * Optional alias for the connection
   * @example "Bob"
   */
  alias?: string | null;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id: string;
  invitation: ConnectionInvitation;
  /**
   * Invitation URL
   * @example "http://192.168.56.101:8020/invite?c_i=eyJAdHlwZSI6Li4ufQ=="
   */
  invitation_url: string;
}

export interface InvitationResult {
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id: string;
  invitation: ConnectionInvitation;
  /**
   * Invitation URL
   * @example "http://192.168.56.101:8020/invite?c_i=eyJAdHlwZSI6Li4ufQ=="
   */
  invitation_url: string;
}

export type IssueCredentialModuleResponse = object;

export interface IssueCredentialRequest {
  credential?: Credential;
  options?: LDProofVCOptions;
}

export interface IssueCredentialResponse {
  verifiableCredential?: VerifiableCredential;
}

export interface IssuerCredRevRecord {
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id?: string;
  /**
   * Credential exchange record identifier at credential issue
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_ex_id?: string;
  /** Credential exchange version */
  cred_ex_version?: string;
  /**
   * Credential revocation identifier
   * @pattern ^[1-9][0-9]*$
   * @example "12345"
   */
  cred_rev_id?: string;
  /**
   * Issuer credential revocation record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  record_id?: string;
  /**
   * Revocation registry identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)
   * @example "WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0"
   */
  rev_reg_id?: string;
  /**
   * Issue credential revocation record state
   * @example "issued"
   */
  state?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface IssuerCredRevRecordSchemaAnonCreds {
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /** Credential definition identifier */
  cred_def_id?: string;
  /**
   * Credential exchange record identifier at credential issue
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_ex_id?: string;
  /** Credential exchange version */
  cred_ex_version?: string;
  /** Credential revocation identifier */
  cred_rev_id?: string;
  /**
   * Issuer credential revocation record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  record_id?: string;
  /** Revocation registry identifier */
  rev_reg_id?: string;
  /**
   * Issue credential revocation record state
   * @example "issued"
   */
  state?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface IssuerRevRegRecord {
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id?: string;
  /**
   * Error message
   * @example "Revocation registry undefined"
   */
  error_msg?: string;
  /**
   * Issuer DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  issuer_did?: string;
  /**
   * Maximum number of credentials for revocation registry
   * @example 1000
   */
  max_cred_num?: number;
  /** Credential revocation identifier for credential revoked and pending publication to ledger */
  pending_pub?: string[];
  /**
   * Issuer revocation registry record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  record_id?: string;
  /**
   * Revocation registry type (specify CL_ACCUM)
   * @example "CL_ACCUM"
   */
  revoc_def_type?: 'CL_ACCUM';
  /** Revocation registry definition */
  revoc_reg_def?: IndyRevRegDef;
  /** Revocation registry entry */
  revoc_reg_entry?: IndyRevRegEntry;
  /**
   * Revocation registry identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)
   * @example "WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0"
   */
  revoc_reg_id?: string;
  /**
   * Issue revocation registry record state
   * @example "active"
   */
  state?: string;
  /** Tag within issuer revocation registry identifier */
  tag?: string;
  /**
   * Tails hash
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44}$
   * @example "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
   */
  tails_hash?: string;
  /** Local path to tails file */
  tails_local_path?: string;
  /** Public URI for tails file */
  tails_public_uri?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface JWSCreate {
  /**
   * DID of interest
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$|^did:([a-zA-Z0-9_]+)(:[a-zA-Z0-9_.%-]+)?:([a-zA-Z0-9_.%-]+(:[a-zA-Z0-9_.%-]+)*)((;[a-zA-Z0-9_.:%-]+=[a-zA-Z0-9_.:%-]*)*)(\/[^#?]*)?([?][^#]*)?(\#.*)?$$
   * @example "did:peer:WgWxqztrNooG92RXvxSTWv"
   */
  did?: string;
  headers?: Record<string, any>;
  payload: Record<string, any>;
  /**
   * Information used for proof verification
   * @pattern \w+:(\/?\/?)[^\s]+
   * @example "did:key:z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL#z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL"
   */
  verificationMethod?: string;
}

export interface JWSVerify {
  /**
   * @pattern ^[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]+$
   * @example "eyJhbGciOiJFZERTQSJ9.eyJhIjogIjAifQ.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
   */
  jwt?: string;
}

export interface JWSVerifyResponse {
  /** Error text */
  error?: string;
  /** Headers from verified JWT. */
  headers: Record<string, any>;
  /** kid of signer */
  kid: string;
  /** Payload from verified JWT */
  payload: Record<string, any>;
  valid: boolean;
}

export interface Keylist {
  /** List of keylist records */
  results?: RouteRecord[];
}

export interface KeylistQuery {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /**
   * Query dictionary object
   * @example {"filter":{}}
   */
  filter?: Record<string, any>;
  /** Pagination info */
  paginate?: KeylistQueryPaginate;
}

export interface KeylistQueryFilterRequest {
  /** Filter for keylist query */
  filter?: Record<string, any>;
}

export interface KeylistQueryPaginate {
  /**
   * Limit for keylist query
   * @example 30
   */
  limit?: number;
  /**
   * Offset value for query
   * @example 0
   */
  offset?: number;
}

export interface KeylistUpdate {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /** List of update rules */
  updates?: KeylistUpdateRule[];
}

export interface KeylistUpdateRequest {
  updates?: KeylistUpdateRule[];
}

export interface KeylistUpdateRule {
  /**
   * Action for specific key
   * @example "add"
   */
  action: 'add' | 'remove';
  /**
   * Key to remove or add
   * @pattern ^did:key:z[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]+$|^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44}$
   * @example "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
   */
  recipient_key: string;
}

export interface LDProofVCDetail {
  /**
   * Detail of the JSON-LD Credential to be issued
   * @example {"@context":["https://www.w3.org/2018/credentials/v1","https://w3id.org/citizenship/v1"],"credentialSubject":{"familyName":"SMITH","gender":"Male","givenName":"JOHN","type":["PermanentResident","Person"]},"description":"Government of Example Permanent Resident Card.","identifier":"83627465","issuanceDate":"2019-12-03T12:19:52Z","issuer":"did:key:z6MkmjY8GnV5i9YTDtPETC2uUAW6ejw3nk5mXF5yci5ab7th","name":"Permanent Resident Card","type":["VerifiableCredential","PermanentResidentCard"]}
   */
  credential: Credential;
  /**
   * Options for specifying how the linked data proof is created.
   * @example {"proofType":"Ed25519Signature2018"}
   */
  options: LDProofVCOptions;
  [key: string]: any;
}

export interface LDProofVCOptions {
  /**
   * A challenge to include in the proof. SHOULD be provided by the requesting party of the credential (=holder)
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  challenge?: string;
  /**
   * The date and time of the proof (with a maximum accuracy in seconds). Defaults to current system time
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created?: string;
  /** The credential status mechanism to use for the credential. Omitting the property indicates the issued credential will not include a credential status */
  credentialStatus?: CredentialStatusOptions;
  /**
   * The intended domain of validity for the proof
   * @example "example.com"
   */
  domain?: string;
  /**
   * The proof purpose used for the proof. Should match proof purposes registered in the Linked Data Proofs Specification
   * @example "assertionMethod"
   */
  proofPurpose?: string;
  /**
   * The proof type used for the proof. Should match suites registered in the Linked Data Cryptographic Suite Registry
   * @example "Ed25519Signature2018"
   */
  proofType?: string;
  /**
   * The verification method to use for the proof. Should match a verification method in the wallet
   * @example "did:example:123456#key-1"
   */
  verificationMethod?: string;
  [key: string]: any;
}

export interface LedgerConfigInstance {
  /** Endorser service alias (optional) */
  endorser_alias?: string;
  /** Endorser DID (optional) */
  endorser_did?: string;
  /**
   * Ledger identifier. Auto-generated UUID4 if not provided
   * @example "f47ac10b-58cc-4372-a567-0e02b2c3d479"
   */
  id: string;
  /** Production-grade ledger (true/false) */
  is_production: boolean;
  /** Write capability enabled (default: False) */
  is_write?: boolean;
  /**
   * Keep-alive timeout in seconds for idle connections
   * @default 5
   */
  keepalive?: number;
  /**
   * Ledger pool name (defaults to ledger ID if not specified)
   * @example "bcovrin-test-pool"
   */
  pool_name?: string;
  /** Read-only access (default: False) */
  read_only?: boolean;
  /** SOCKS proxy URL (optional) */
  socks_proxy?: string;
}

export interface LedgerConfigList {
  /** Non-production ledgers (may be empty) */
  non_production_ledgers: LedgerConfigInstance[];
  /** Production ledgers (may be empty) */
  production_ledgers: LedgerConfigInstance[];
}

export type LedgerModulesResult = object;

export interface LinkedDataProof {
  /**
   * Associates a challenge with a proof, for use with a proofPurpose such as authentication
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  challenge?: string;
  /**
   * The string value of an ISO8601 combined date and time string generated by the Signature Algorithm
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created?: string;
  /**
   * A string value specifying the restricted domain of the signature.
   * @example "https://example.com"
   */
  domain?: string;
  /**
   * Associates a Detached Json Web Signature with a proof
   * @example "eyJhbGciOiAiRWREUc2UsICJjcml0IjogWyJiNjQiXX0..lKJU0Df_keblRKhZAS9Qq6zybm-HqUXNVZ8vgEPNTAjQ1Ch6YBKY7UBAjg6iBX5qBQ"
   */
  jws?: string;
  /**
   * The nonce
   * @example "CF69iO3nfvqRsRBNElE8b4wO39SyJHPM7Gg1nExltW5vSfQA1lvDCR/zXX1To0/4NLo=="
   */
  nonce?: string;
  /**
   * Proof purpose
   * @example "assertionMethod"
   */
  proofPurpose: string;
  /**
   * The proof value of a proof
   * @example "sy1AahqbzJQ63n9RtekmwzqZeVj494VppdAVJBnMYrTwft6cLJJGeTSSxCCJ6HKnRtwE7jjDh6sB2z2AAiZY9BBnCD8wUVgwqH3qchGRCuC2RugA4eQ9fUrR4Yuycac3caiaaay"
   */
  proofValue?: string;
  /**
   * Identifies the digital signature suite that was used to create the signature
   * @example "Ed25519Signature2018"
   */
  type: string;
  /**
   * Information used for proof verification
   * @pattern \w+:(\/?\/?)[^\s]+
   * @example "did:key:z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL#z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL"
   */
  verificationMethod: string;
  [key: string]: any;
}

export interface ListCredentialsResponse {
  results?: VerifiableCredential[];
}

export interface MaybeStoredConnectionsRecord {
  /**
   * Connection acceptance: manual or auto
   * @example "auto"
   */
  accept?: 'manual' | 'auto';
  /**
   * Optional alias to apply to connection for later use
   * @example "Bob, providing quotes"
   */
  alias?: string;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id?: string;
  connection_protocol?:
    | 'connections/1.0'
    | 'didexchange/1.0'
    | 'didexchange/1.1';
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Error message
   * @example "No DIDDoc provided; cannot connect to public DID"
   */
  error_msg?: string;
  /**
   * Inbound routing connection id to use
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  inbound_connection_id?: string;
  /**
   * Public key for connection
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{43,44}$
   * @example "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
   */
  invitation_key?: string;
  /**
   * Invitation mode
   * @example "once"
   */
  invitation_mode?: 'once' | 'multi' | 'static';
  /**
   * ID of out-of-band invitation message
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  invitation_msg_id?: string;
  /**
   * Our DID for connection
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$|^did:([a-zA-Z0-9_]+)(:[a-zA-Z0-9_.%-]+)?:([a-zA-Z0-9_.%-]+(:[a-zA-Z0-9_.%-]+)*)((;[a-zA-Z0-9_.:%-]+=[a-zA-Z0-9_.:%-]*)*)(\/[^#?]*)?([?][^#]*)?(\#.*)?$$
   * @example "did:peer:WgWxqztrNooG92RXvxSTWv"
   */
  my_did?: string;
  /**
   * Connection request identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  request_id?: string;
  /**
   * State per RFC 23
   * @example "invitation-sent"
   */
  rfc23_state?: string;
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Their DID for connection
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$|^did:([a-zA-Z0-9_]+)(:[a-zA-Z0-9_.%-]+)?:([a-zA-Z0-9_.%-]+(:[a-zA-Z0-9_.%-]+)*)((;[a-zA-Z0-9_.:%-]+=[a-zA-Z0-9_.:%-]*)*)(\/[^#?]*)?([?][^#]*)?(\#.*)?$$
   * @example "did:peer:WgWxqztrNooG92RXvxSTWv"
   */
  their_did?: string;
  /**
   * Their label for connection
   * @example "Bob"
   */
  their_label?: string;
  /**
   * Other agent's public DID for connection
   * @example "2cpBmR3FqGKWi5EyUbpRY8"
   */
  their_public_did?: string;
  /**
   * Their role in the connection protocol
   * @example "requester"
   */
  their_role?: 'invitee' | 'requester' | 'inviter' | 'responder';
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export type MediationCreateRequest = object;

export interface MediationDeny {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
}

export interface MediationGrant {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /**
   * endpoint on which messages destined for the recipient are received.
   * @example "http://192.168.56.102:8020/"
   */
  endpoint?: string;
  routing_keys?: string[];
}

export interface MediationIdMatchInfo {
  /**
   * Mediation record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  mediation_id: string;
}

export interface MediationList {
  /** List of mediation records */
  results: MediationRecord[];
}

export interface MediationRecord {
  connection_id: string;
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  endpoint?: string;
  mediation_id?: string;
  mediator_terms?: string[];
  recipient_terms?: string[];
  role: string;
  routing_keys?: string[];
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface Menu {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /**
   * Introductory text for the menu
   * @example "This menu presents options"
   */
  description?: string;
  /**
   * An optional error message to display in menu header
   * @example "Error: item not found"
   */
  errormsg?: string;
  /** List of menu options */
  options: MenuOption[];
  /**
   * Menu title
   * @example "My Menu"
   */
  title?: string;
}

export interface MenuForm {
  /**
   * Additional descriptive text for menu form
   * @example "Window preference settings"
   */
  description?: string;
  /** List of form parameters */
  params?: MenuFormParam[];
  /**
   * Alternative label for form submit button
   * @example "Send"
   */
  'submit-label'?: string;
  /**
   * Menu form title
   * @example "Preferences"
   */
  title?: string;
}

export interface MenuFormParam {
  /**
   * Default parameter value
   * @example "0"
   */
  default?: string;
  /**
   * Additional descriptive text for menu form parameter
   * @example "Delay in seconds before starting"
   */
  description?: string;
  /**
   * Menu parameter name
   * @example "delay"
   */
  name: string;
  /**
   * Whether parameter is required
   * @example "False"
   */
  required?: boolean;
  /**
   * Menu parameter title
   * @example "Delay in seconds"
   */
  title: string;
  /**
   * Menu form parameter input type
   * @example "int"
   */
  type?: string;
}

export interface MenuJson {
  /**
   * Introductory text for the menu
   * @example "User preferences for window settings"
   */
  description?: string;
  /**
   * Optional error message to display in menu header
   * @example "Error: item not present"
   */
  errormsg?: string;
  /** List of menu options */
  options: MenuOption[];
  /**
   * Menu title
   * @example "My Menu"
   */
  title?: string;
}

export interface MenuOption {
  /**
   * Additional descriptive text for menu option
   * @example "Window display preferences"
   */
  description?: string;
  /**
   * Whether to show option as disabled
   * @example "False"
   */
  disabled?: boolean;
  form?: MenuForm;
  /**
   * Menu option name (unique identifier)
   * @example "window_prefs"
   */
  name: string;
  /**
   * Menu option title
   * @example "Window Preferences"
   */
  title: string;
}

export type MultitenantModuleResponse = object;

export interface OcaRecord {
  /** OCA Bundle */
  bundle?: Record<string, any>;
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Cred Def identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id?: string;
  /**
   * OCA Record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  oca_id: string;
  /** Public DID of OCA record owner */
  owner_did?: string;
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id?: string;
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
  /** (Public) Url for OCA Bundle */
  url?: string;
}

export interface OcaRecordList {
  /** List of OCA records */
  results?: OcaRecord[];
}

export interface OcaRecordOperationResponse {
  /** True if operation successful, false if otherwise */
  success: boolean;
}

export interface OobRecord {
  /**
   * Connection record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  attach_thread_id?: string;
  /**
   * Connection record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id?: string;
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Invitation message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  invi_msg_id: string;
  /** Out of band invitation message */
  invitation: InvitationMessage;
  /**
   * Allow for multiple uses of the oob invitation
   * @example true
   */
  multi_use?: boolean;
  /**
   * Oob record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  oob_id: string;
  /**
   * Recipient key used for oob invitation
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  our_recipient_key?: string;
  /**
   * OOB Role
   * @example "receiver"
   */
  role?: 'sender' | 'receiver';
  /**
   * Out of band message exchange state
   * @example "await-response"
   */
  state:
    | 'initial'
    | 'prepare-response'
    | 'await-response'
    | 'reuse-not-accepted'
    | 'reuse-accepted'
    | 'done'
    | 'deleted';
  their_service?: ServiceDecorator;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface PerformRequest {
  /**
   * Menu option name
   * @example "Query"
   */
  name?: string;
  /** Input parameter values */
  params?: Record<string, string>;
}

export interface PingRequest {
  /** Comment for the ping message */
  comment?: string | null;
}

export interface PingRequestResponse {
  /** Thread ID of the ping message */
  thread_id?: string;
}

export interface PluginCreateWalletRequest {
  /** Agent config key-value pairs */
  extra_settings?: Record<string, any>;
  /**
   * Image url for this wallet. This image url is publicized (self-attested) to other agents as part of forming a connection.
   * @example "https://aries.ca/images/sample.png"
   */
  image_url?: string;
  /**
   * Key management method to use for this wallet.
   * @example "managed"
   */
  key_management_mode?: 'managed';
  /**
   * Label for this wallet. This label is publicized (self-attested) to other agents as part of forming a connection.
   * @example "Alice"
   */
  label?: string;
  /**
   * Webhook target dispatch type for this wallet. default: Dispatch only to webhooks associated with this wallet. base: Dispatch only to webhooks associated with the base wallet. both: Dispatch to both webhook targets.
   * @example "default"
   */
  wallet_dispatch_type?: 'default' | 'both' | 'base';
  /**
   * Master key used for key derivation.
   * @example "MySecretKey123"
   */
  wallet_key?: string;
  /**
   * Key derivation
   * @example "RAW"
   */
  wallet_key_derivation?: 'ARGON2I_MOD' | 'ARGON2I_INT' | 'RAW';
  /**
   * Wallet name
   * @example "MyNewWallet"
   */
  wallet_name?: string;
  /**
   * Type of the wallet to create. Must be same as base wallet.
   * @example "askar"
   */
  wallet_type?: 'askar' | 'askar-anoncreds';
  /** List of Webhook URLs associated with this subwallet */
  wallet_webhook_urls?: string[];
}

export interface Presentation {
  /**
   * The JSON-LD context of the presentation
   * @example ["https://www.w3.org/2018/credentials/v1"]
   */
  '@context': any[];
  /**
   * The JSON-LD Verifiable Credential Holder. Either string of object with id field.
   * @example "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
   */
  holder?: any;
  /**
   * The ID of the presentation
   * @pattern \w+:(\/?\/?)[^\s]+
   * @example "http://example.edu/presentations/1872"
   */
  id?: string;
  /**
   * The proof of the presentation
   * @example {"created":"2019-12-11T03:50:55","jws":"eyJhbGciOiAiRWREU0EiLCAiYjY0IjogZmFsc2UsICJjcml0JiNjQiXX0..lKJU0Df_keblRKhZAS9Qq6zybm-HqUXNVZ8vgEPNTAjQKBhQDxvXNo7nvtUBb_Eq1Ch6YBKY5qBQ","proofPurpose":"assertionMethod","type":"Ed25519Signature2018","verificationMethod":"did:key:z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL#z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL"}
   */
  proof?: LinkedDataProof;
  /**
   * The JSON-LD type of the presentation
   * @example ["VerifiablePresentation"]
   */
  type: string[];
  verifiableCredential?: Record<string, any>[];
  [key: string]: any;
}

export interface PresentationDefinition {
  format?: ClaimFormat;
  /**
   * Unique Resource Identifier
   * @pattern [a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  id?: string;
  input_descriptors?: InputDescriptors[];
  /** Human-friendly name that describes what the presentation definition pertains to */
  name?: string;
  /** Describes the purpose for which the Presentation Definition's inputs are being requested */
  purpose?: string;
  submission_requirements?: SubmissionRequirements[];
}

export interface PresentationProposal {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /** Human-readable comment */
  comment?: string | null;
  presentation_proposal: IndyPresPreview;
}

export interface PresentationRequest {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /** Human-readable comment */
  comment?: string | null;
  'request_presentations~attach': AttachDecorator[];
}

export interface PresentationVerificationResult {
  credential_results?: DocumentVerificationResult[];
  errors?: string[];
  presentation_result?: DocumentVerificationResult;
  verified: boolean;
}

export interface ProfileSettings {
  /**
   * Profile settings dict
   * @example {"debug.invite_public":true,"log.level":"INFO","public_invites":false}
   */
  settings?: Record<string, any>;
}

export interface ProofResult {
  error?: string;
  proof?: Record<string, any>;
  purpose_result?: PurposeResult;
  verified?: boolean;
}

export interface ProtocolDescriptor {
  pid: string;
  /** List of roles */
  roles?: string[] | null;
}

export interface ProvePresentationRequest {
  options?: LDProofVCOptions;
  presentation?: Presentation;
}

export interface ProvePresentationResponse {
  verifiablePresentation?: VerifiablePresentation;
}

export interface PublishRevocations {
  /** Credential revocation ids by revocation registry id */
  rrid2crid?: Record<string, string[]>;
}

export interface PublishRevocationsOptions {
  /**
   * Create transaction for endorser (optional, default false). Use this for agents who don't specify an author role but want to create a transaction for an endorser to sign.
   * @example false
   */
  create_transaction_for_endorser?: boolean;
  /**
   * Connection identifier (optional) (this is an example). You can set this if you know the endorser's connection id you want to use. If not specified then the agent will attempt to find an endorser connection.
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  endorser_connection_id?: string;
}

export interface PublishRevocationsResultSchemaAnonCreds {
  /** Credential revocation ids by revocation registry id */
  rrid2crid?: Record<string, string[]>;
}

export interface PublishRevocationsSchemaAnonCreds {
  options?: PublishRevocationsOptions;
  /** Credential revocation ids by revocation registry id */
  rrid2crid?: Record<string, string[]>;
}

export interface PurposeResult {
  controller?: Record<string, any>;
  error?: string;
  valid?: boolean;
}

export interface Queries {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  queries?: QueryItem[];
}

export interface Query {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  comment?: string | null;
  query: string;
}

export interface QueryItem {
  /** feature type */
  'feature-type': 'protocol' | 'goal-code';
  /** match */
  match: string;
}

export interface RawEncoded {
  /**
   * Encoded value
   * @pattern ^-?[0-9]*$
   * @example "-1"
   */
  encoded?: string;
  /** Raw value */
  raw?: string;
}

export interface ReceiveInvitationRequest {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /**
   * DID for connection invitation
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$|^did:([a-zA-Z0-9_]+)(:[a-zA-Z0-9_.%-]+)?:([a-zA-Z0-9_.%-]+(:[a-zA-Z0-9_.%-]+)*)((;[a-zA-Z0-9_.:%-]+=[a-zA-Z0-9_.:%-]*)*)(\/[^#?]*)?([?][^#]*)?(\#.*)?$$
   * @example "did:peer:WgWxqztrNooG92RXvxSTWv"
   */
  did?: string;
  /**
   * Optional image URL for connection invitation
   * @format url
   * @example "http://192.168.56.101/img/logo.jpg"
   */
  imageUrl?: string | null;
  /**
   * Optional label for connection invitation
   * @example "Bob"
   */
  label?: string;
  /** List of recipient keys */
  recipientKeys?: string[];
  /** List of routing keys */
  routingKeys?: string[];
  /**
   * Service endpoint at which to reach this agent
   * @example "http://192.168.56.101:8020"
   */
  serviceEndpoint?: string;
}

export interface RemoveWalletRequest {
  /**
   * Master key used for key derivation. Only required for unmanaged wallets.
   * @example "MySecretKey123"
   */
  wallet_key?: string;
}

export interface ReservationApproveRequest {
  /**
   * Reason(s) for approving a tenant reservation
   * @example "Welcome"
   */
  state_notes?: string;
}

export interface ReservationApproveResponse {
  /** The reservation password - deliver to tenant contact */
  reservation_pwd: string;
}

export interface ReservationDenyRequest {
  /**
   * Reason(s) for approving or denying a tenant reservation
   * @example "No room at the inn."
   */
  state_notes: string;
}

export interface ReservationList {
  /** Authorization token to authenticate wallet requests */
  results?: ReservationRecord[];
}

export interface ReservationRecord {
  /** @example "{"endorser_alias": " ... ", "ledger_id": " ... "}" */
  connect_to_endorser?: Record<string, any>[];
  /** Contact email for this tenant request */
  contact_email: string;
  /** Contact name for this tenant request */
  contact_name: string;
  /** Contact phone number for this tenant request */
  contact_phone: string;
  /**
   * Context data for this tenant request
   * @example "{"tenant_reason": " ... ", "contact_name": " ... ", "contact_phone": " ... "}"
   */
  context_data?: Record<string, any>;
  create_public_did?: string[];
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Tenant Reservation Record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  reservation_id: string;
  /**
   * The state of the tenant request.
   * @example "requested"
   */
  state: 'requested' | 'approved' | 'checked_in';
  /** Notes about the state of the tenant request */
  state_notes?: string;
  /**
   * Tenant Record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  tenant_id?: string;
  /**
   * Proposed name of Tenant
   * @example "line of business short name"
   */
  tenant_name: string;
  /**
   * Reason(s) for requesting a tenant
   * @example "Issue permits to clients"
   */
  tenant_reason: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
  /**
   * Tenant Wallet Record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  wallet_id?: string;
}

export type ReservationRefresh = object;

export interface ReservationRequest {
  /** Contact email for this tenant request */
  contact_email: string;
  /**
   * Optional context data for this tenant request
   * @example {"contact_phone":"555-555-5555"}
   */
  context_data?: Record<string, any>;
  /**
   * Proposed name of Tenant
   * @example "line of business short name"
   */
  tenant_name: string;
}

export interface ReservationResponse {
  /**
   * The reservation record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  reservation_id: string;
}

export interface ResolutionResult {
  /** DID Document */
  did_document: Record<string, any>;
  /** Resolution metadata */
  metadata: Record<string, any>;
}

export interface RevList {
  /**
   * The current accumulator value
   * @example "21 118...1FB"
   */
  currentAccumulator?: string;
  /**
   * Issuer Identifier of the credential definition or schema
   * @example "did:(method):WgWxqztrNooG92RXvxSTWv"
   */
  issuerId?: string;
  /**
   * The ID of the revocation registry definition
   * @example "did:(method):4:did:<method>:3:CL:20:tag:CL_ACCUM:0"
   */
  revRegDefId?: string;
  /**
   * Bit list representing revoked credentials
   * @example [0,1,1,0]
   */
  revocationList?: number[];
  /**
   * Timestamp at which revocation list is applicable
   * @example "2021-12-31T23:59:59Z"
   */
  timestamp?: number;
}

export interface RevListCreateRequest {
  options?: RevListOptions;
  /**
   * Revocation registry definition identifier
   * @example "did:(method):4:did:<method>:3:CL:20:tag:CL_ACCUM:0"
   */
  rev_reg_def_id: string;
}

export interface RevListOptions {
  /**
   * Create transaction for endorser (optional, default false). Use this for agents who don't specify an author role but want to create a transaction for an endorser to sign.
   * @example false
   */
  create_transaction_for_endorser?: boolean;
  /**
   * Connection identifier (optional) (this is an example). You can set this if you know the endorser's connection id you want to use. If not specified then the agent will attempt to find an endorser connection.
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  endorser_connection_id?: string;
}

export interface RevListResult {
  job_id?: string;
  registration_metadata?: Record<string, any>;
  revocation_list_metadata?: Record<string, any>;
  revocation_list_state?: RevListState;
}

export interface RevListState {
  /** revocation list */
  revocation_list?: RevList;
  state?: 'finished' | 'failed' | 'action' | 'wait';
}

export interface RevRegCreateRequest {
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  credential_definition_id?: string;
  /**
   * Revocation registry size
   * @min 4
   * @max 32768
   * @example 1000
   */
  max_cred_num?: number;
}

export interface RevRegCreateRequestSchemaAnonCreds {
  options?: RevRegDefOptions;
  revocation_registry_definition?: InnerRevRegDef;
}

export interface RevRegDef {
  /**
   * Credential definition identifier
   * @example "did:(method):3:CL:20:tag"
   */
  credDefId?: string;
  /**
   * Issuer Identifier of the credential definition or schema
   * @example "did:(method):WgWxqztrNooG92RXvxSTWv"
   */
  issuerId?: string;
  revocDefType?: string;
  /**
   * tag for the revocation registry definition
   * @example "default"
   */
  tag?: string;
  value?: RevRegDefValue;
}

export interface RevRegDefOptions {
  /**
   * Create transaction for endorser (optional, default false). Use this for agents who don't specify an author role but want to create a transaction for an endorser to sign.
   * @example false
   */
  create_transaction_for_endorser?: boolean;
  /**
   * Connection identifier (optional) (this is an example). You can set this if you know the endorser's connection id you want to use. If not specified then the agent will attempt to find an endorser connection.
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  endorser_connection_id?: string;
}

export interface RevRegDefResult {
  job_id?: string;
  registration_metadata?: Record<string, any>;
  revocation_registry_definition_metadata?: Record<string, any>;
  revocation_registry_definition_state?: RevRegDefState;
}

export interface RevRegDefState {
  /** revocation registry definition */
  revocation_registry_definition?: RevRegDef;
  /**
   * revocation registry definition id
   * @example "did:(method):4:did:<method>:3:CL:20:tag:CL_ACCUM:0"
   */
  revocation_registry_definition_id?: string;
  state?: 'finished' | 'failed' | 'action' | 'wait' | 'decommissioned' | 'full';
}

export interface RevRegDefValue {
  /** @example 777 */
  maxCredNum?: number;
  /** @example "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV" */
  publicKeys?: Record<string, any>;
  /** @example "7Qen9RDyemMuV7xGQvp7NjwMSpyHieJyBakycxN7dX7P" */
  tailsHash?: string;
  /** @example "https://tails-server.com/hash/7Qen9RDyemMuV7xGQvp7NjwMSpyHieJyBakycxN7dX7P" */
  tailsLocation?: string;
}

export interface RevRegIssuedResult {
  /**
   * Number of credentials issued against revocation registry
   * @min 0
   * @example 0
   */
  result?: number;
}

export interface RevRegIssuedResultSchemaAnonCreds {
  /**
   * Number of credentials issued against revocation registry
   * @min 0
   * @example 0
   */
  result?: number;
}

export interface RevRegResult {
  result?: IssuerRevRegRecord;
}

export interface RevRegResultSchemaAnonCreds {
  result?: IssuerRevRegRecord;
}

export interface RevRegUpdateTailsFileUri {
  /**
   * Public URI to the tails file
   * @format url
   * @example "http://192.168.56.133:6543/revocation/registry/WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0/tails-file"
   */
  tails_public_uri: string;
}

export interface RevRegWalletUpdatedResult {
  /** Calculated accumulator for phantom revocations */
  accum_calculated?: Record<string, any>;
  /** Applied ledger transaction to fix revocations */
  accum_fixed?: Record<string, any>;
  /** Indy revocation registry delta */
  rev_reg_delta?: Record<string, any>;
}

export interface RevRegWalletUpdatedResultSchemaAnonCreds {
  /** Calculated accumulator for phantom revocations */
  accum_calculated?: Record<string, any>;
  /** Applied ledger transaction to fix revocations */
  accum_fixed?: Record<string, any>;
  /** Indy revocation registry delta */
  rev_reg_delta?: Record<string, any>;
}

export interface RevRegsCreated {
  rev_reg_ids?: string[];
}

export interface RevRegsCreatedSchemaAnonCreds {
  rev_reg_ids?: string[];
}

export type RevocationModuleResponse = object;

export interface RevokeRequest {
  /** Optional comment to include in revocation notification */
  comment?: string;
  /**
   * Connection ID to which the revocation notification will be sent; required if notify is true
   * @pattern [a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id?: string;
  /**
   * Credential exchange identifier
   * @pattern [a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_ex_id?: string;
  /**
   * Credential revocation identifier
   * @pattern ^[1-9][0-9]*$
   * @example "12345"
   */
  cred_rev_id?: string;
  /** Send a notification to the credential recipient */
  notify?: boolean;
  /** Specify which version of the revocation notification should be sent */
  notify_version?: 'v1_0' | 'v2_0';
  /** (True) publish revocation to ledger immediately, or (default, False) mark it pending */
  publish?: boolean;
  /**
   * Revocation registry identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)
   * @example "WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0"
   */
  rev_reg_id?: string;
  /** Thread ID of the credential exchange message thread resulting in the credential now being revoked; required if notify is true */
  thread_id?: string;
}

export interface RevokeRequestSchemaAnonCreds {
  /** Optional comment to include in revocation notification */
  comment?: string;
  /**
   * Connection ID to which the revocation notification will be sent; required if notify is true
   * @pattern [a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id?: string;
  /**
   * Credential exchange identifier
   * @pattern [a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_ex_id?: string;
  /**
   * Credential revocation identifier
   * @pattern ^[1-9][0-9]*$
   * @example "12345"
   */
  cred_rev_id?: string;
  /** Send a notification to the credential recipient */
  notify?: boolean;
  /** Specify which version of the revocation notification should be sent */
  notify_version?: 'v1_0' | 'v2_0';
  /** (True) publish revocation to ledger immediately, or (default, False) mark it pending */
  publish?: boolean;
  /**
   * Revocation registry identifier
   * @pattern ^(.+$)
   * @example "did:(method):4:did:<method>:3:CL:20:tag:CL_ACCUM:0"
   */
  rev_reg_id?: string;
  /** Thread ID of the credential exchange message thread resulting in the credential now being revoked; required if notify is true */
  thread_id?: string;
}

export interface Rotate {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /**
   * The DID the rotating party is rotating to
   * @example "did:example:newdid"
   */
  to_did: string;
}

export interface RouteRecord {
  connection_id?: string;
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  recipient_key: string;
  record_id?: string;
  role?: string;
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
  wallet_id?: string;
}

export interface SDJWSCreate {
  /**
   * DID of interest
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$|^did:([a-zA-Z0-9_]+)(:[a-zA-Z0-9_.%-]+)?:([a-zA-Z0-9_.%-]+(:[a-zA-Z0-9_.%-]+)*)((;[a-zA-Z0-9_.:%-]+=[a-zA-Z0-9_.:%-]*)*)(\/[^#?]*)?([?][^#]*)?(\#.*)?$$
   * @example "did:peer:WgWxqztrNooG92RXvxSTWv"
   */
  did?: string;
  headers?: Record<string, any>;
  non_sd_list?: string[];
  payload: Record<string, any>;
  /**
   * Information used for proof verification
   * @pattern \w+:(\/?\/?)[^\s]+
   * @example "did:key:z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL#z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL"
   */
  verificationMethod?: string;
}

export interface SDJWSVerify {
  /**
   * @pattern ^[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]+(?:~[a-zA-Z0-9._-]+)*~?$
   * @example "eyJhbGciOiJFZERTQSJ9.eyJhIjogIjAifQ.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk~WyJEM3BUSFdCYWNRcFdpREc2TWZKLUZnIiwgIkRFIl0~WyJPMTFySVRjRTdHcXExYW9oRkd0aDh3IiwgIlNBIl0~WyJkVmEzX1JlTGNsWTU0R1FHZm5oWlRnIiwgInVwZGF0ZWRfYXQiLCAxNTcwMDAwMDAwXQ"
   */
  sd_jwt?: string;
}

export interface SDJWSVerifyResponse {
  /**
   * Disclosure arrays associated with the SD-JWT
   * @example [["fx1iT_mETjGiC-JzRARnVg","name","Alice"],["n4-t3mlh8jSS6yMIT7QHnA","street_address",{"_sd":["kLZrLK7enwfqeOzJ9-Ss88YS3mhjOAEk9lr_ix2Heng"]}]]
   */
  disclosures?: any[][];
  /** Error text */
  error?: string;
  /** Headers from verified JWT. */
  headers: Record<string, any>;
  /** kid of signer */
  kid: string;
  /** Payload from verified JWT */
  payload: Record<string, any>;
  valid: boolean;
}

export interface Schema {
  /** Schema attribute names */
  attrNames?: string[];
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  id?: string;
  /**
   * Schema name
   * @example "schema_name"
   */
  name?: string;
  /**
   * Schema sequence number
   * @min 1
   * @example 10
   */
  seqNo?: number;
  /**
   * Node protocol version
   * @pattern ^[0-9.]+$
   * @example "1.0"
   */
  ver?: string;
  /**
   * Schema version
   * @pattern ^[0-9.]+$
   * @example "1.0"
   */
  version?: string;
}

export interface SchemaGetResult {
  schema?: Schema;
}

export interface SchemaInputDescriptor {
  /** Required */
  required?: boolean;
  /** URI */
  uri?: string;
}

export interface SchemaPostOption {
  /**
   * Create transaction for endorser (optional, default false). Use this for agents who don't specify an author role but want to create a transaction for an endorser to sign.
   * @example false
   */
  create_transaction_for_endorser?: boolean;
  /**
   * Connection identifier (optional) (this is an example). You can set this if you know the endorser's connection id you want to use. If not specified then the agent will attempt to find an endorser connection.
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  endorser_connection_id?: string;
}

export interface SchemaPostRequest {
  options?: SchemaPostOption;
  schema?: AnonCredsSchema;
}

export interface SchemaResult {
  job_id?: string;
  registration_metadata?: Record<string, any>;
  schema_metadata?: Record<string, any>;
  schema_state?: SchemaState;
}

export interface SchemaSendRequest {
  /** List of schema attributes */
  attributes: string[];
  /**
   * Schema name
   * @example "prefs"
   */
  schema_name: string;
  /**
   * Schema version
   * @pattern ^[0-9.]+$
   * @example "1.0"
   */
  schema_version: string;
}

export interface SchemaSendResult {
  /** Schema definition */
  schema?: Schema;
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id: string;
}

export interface SchemaState {
  schema?: AnonCredsSchema;
  /**
   * Schema identifier
   * @example "did:(method):2:schema_name:1.0"
   */
  schema_id?: string;
  state?: 'finished' | 'failed' | 'action' | 'wait';
}

export interface SchemaStorageAdd {
  /** Schema identifier */
  schema_id: string;
}

export interface SchemaStorageList {
  /** List of schema storage records */
  results?: SchemaStorageRecord[];
}

export interface SchemaStorageOperationResponse {
  /** True if operation successful, false if otherwise */
  success: boolean;
}

export interface SchemaStorageRecord {
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /** Schema identifier */
  ledger_id?: string;
  /** (Indy) schema */
  schema?: Record<string, any>;
  /** Serialized schema */
  schema_dict?: Record<string, any>;
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id: string;
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface SchemasCreatedResult {
  schema_ids?: string[];
}

export interface SchemasInputDescriptorFilter {
  /** oneOf */
  oneof_filter?: boolean;
  uri_groups?: SchemaInputDescriptor[][];
}

export interface SendMenu {
  /** Menu to send to connection */
  menu: MenuJson;
}

export interface SendMessage {
  /**
   * Message content
   * @example "Hello"
   */
  content?: string;
}

export interface ServiceDecorator {
  /** List of recipient keys */
  recipientKeys: string[];
  /** List of routing keys */
  routingKeys?: string[];
  /**
   * Service endpoint at which to reach this agent
   * @example "http://192.168.56.101:8020"
   */
  serviceEndpoint: string;
}

export interface SignRequest {
  doc: Doc;
  /** Verkey to use for signing */
  verkey: string;
}

export interface SignResponse {
  /** Error text */
  error?: string;
  /** Signed document */
  signed_doc?: Record<string, any>;
}

export interface SignatureOptions {
  challenge?: string;
  domain?: string;
  proofPurpose: string;
  type?: string;
  verificationMethod: string;
}

export interface SignedDoc {
  /** Linked data proof */
  proof: SignatureOptions;
  [key: string]: any;
}

export interface StoreCredentialRequest {
  verifiableCredential?: VerifiableCredential;
}

export interface StoreCredentialResponse {
  credentialId?: string;
}

export interface SubmissionRequirements {
  /**
   * Count Value
   * @example 1234
   */
  count?: number;
  /** From */
  from?: string;
  from_nested?: SubmissionRequirements[];
  /**
   * Max Value
   * @example 1234
   */
  max?: number;
  /**
   * Min Value
   * @example 1234
   */
  min?: number;
  /** Name */
  name?: string;
  /** Purpose */
  purpose?: string;
  /** Selection */
  rule?: 'all' | 'pick';
}

export interface TAAAccept {
  mechanism?: string;
  text?: string;
  version?: string;
}

export interface TAAAcceptance {
  mechanism?: string;
  /**
   * @min 0
   * @max 18446744073709552000
   * @example 1640995199
   */
  time?: number;
}

export interface TAAInfo {
  aml_record?: AMLRecord;
  taa_accepted?: TAAAcceptance;
  taa_record?: TAARecord;
  taa_required?: boolean;
}

export interface TAARecord {
  digest?: string;
  text?: string;
  version?: string;
}

export interface TAAResult {
  result?: TAAInfo;
}

export interface TailsDeleteResponse {
  message?: string;
}

export interface TenantApiKeyRequest {
  /**
   * Alias/label
   * @example "API key for my Tenant"
   */
  alias: string;
}

export interface TenantAuthenticationApiList {
  /** List of reservations */
  results?: TenantAuthenticationApiRecord[];
}

export interface TenantAuthenticationApiOperationResponse {
  /** True if operation successful, false if otherwise */
  success: boolean;
}

export interface TenantAuthenticationApiRecord {
  /** Alias description for this API key */
  alias: string;
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Tenant Authentication API Record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  tenant_authentication_api_id: string;
  /**
   * Tenant Record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  tenant_id?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface TenantAuthenticationsApiRequest {
  /**
   * Alias/label
   * @example "API key for sample line of business"
   */
  alias: string;
  /**
   * Tenant ID
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  tenant_id: string;
}

export interface TenantAuthenticationsApiResponse {
  /**
   * The API key
   * @example "3bd14a1e8fb645ddadf9913c0922ff3b"
   */
  api_key: string;
  /**
   * The API key record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  tenant_authentication_api_id: string;
}

export interface TenantConfig {
  /** True if tenant can make itself issuer, false if only innkeeper can */
  auto_issuer?: boolean;
  /** Endorser config */
  connect_to_endorser?: EndorserLedgerConfig[];
  /** Public DID config */
  create_public_did?: string[];
  /** Current ledger identifier */
  curr_ledger_id?: string;
  /** True if tenant can switch endorser/ledger */
  enable_ledger_switch?: boolean;
}

export interface TenantLedgerIdConfig {
  /** Ledger identifier */
  ledger_id: string;
}

export interface TenantList {
  /** List of tenants */
  results?: TenantRecord[];
}

export interface TenantRecord {
  /** True if tenant can make itself issuer, false if only innkeeper can */
  auto_issuer?: boolean;
  /** @example "{"endorser_alias": " ... ", "ledger_id": " ... "}" */
  connect_to_endorser?: Record<string, any>[];
  /**
   * Email used to contact this Tenant
   * @example "tmp@emailserver.com"
   */
  contact_email: string;
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  created_public_did?: string[];
  /** Current ledger identifier */
  curr_ledger_id?: string;
  /**
   * Timestamp of the deletion
   * @example "2023-10-30T01:01:01Z"
   */
  deleted_at?: string;
  /** True if tenant can switch endorser/ledger */
  enable_ledger_switch?: boolean;
  /**
   * The state of the tenant.
   * @example "active"
   */
  state: 'active' | 'deleted';
  /**
   * Tenant Record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  tenant_id: string;
  /**
   * Proposed name of Tenant
   * @example "line of business short name"
   */
  tenant_name: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
  /**
   * Tenant Wallet Record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  wallet_id?: string;
}

export interface TransactionJobs {
  /** My transaction related job */
  transaction_my_job?: 'TRANSACTION_AUTHOR' | 'TRANSACTION_ENDORSER' | 'reset';
  /** Their transaction related job */
  transaction_their_job?:
    | 'TRANSACTION_AUTHOR'
    | 'TRANSACTION_ENDORSER'
    | 'reset';
}

export interface TransactionList {
  /** List of transaction records */
  results?: TransactionRecord[];
}

export interface TransactionRecord {
  /**
   * Transaction type
   * @example "101"
   */
  _type?: string;
  /**
   * The connection identifier for this particular transaction record
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id?: string;
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Request Endorser to write the ledger transaction, this parameter is deprecated and no longer supported.
   * @example false
   */
  endorser_write_txn?: boolean;
  formats?: Record<string, string>[];
  messages_attach?: Record<string, any>[];
  /** @example {"context":{"param1":"param1_value","param2":"param2_value"},"post_process":[{"topic":"topic_value","other":"other_value"}]} */
  meta_data?: Record<string, any>;
  signature_request?: Record<string, any>[];
  signature_response?: Record<string, any>[];
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Thread Identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  thread_id?: string;
  /** @example {"expires_time":"2020-12-13T17:29:06+0000"} */
  timing?: Record<string, any>;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
  /**
   * Transaction identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  transaction_id?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface TxnOrCredentialDefinitionSendResult {
  sent?: CredentialDefinitionSendResult;
  /** Credential definition transaction to endorse */
  txn?: TransactionRecord;
}

export interface TxnOrPublishRevocationsResult {
  /** Credential revocation ids by revocation registry id */
  rrid2crid?: Record<string, string[]>;
  txn?: TransactionRecord[];
}

export interface TxnOrRegisterLedgerNymResponse {
  /**
   * Success of nym registration operation
   * @example true
   */
  success?: boolean;
  /** DID transaction to endorse */
  txn?: TransactionRecord;
}

export interface TxnOrRevRegResult {
  sent?: RevRegResult;
  /** Revocation registry definition transaction to endorse */
  txn?: TransactionRecord;
}

export interface TxnOrSchemaSendResult {
  /** Content sent */
  sent?: SchemaSendResult;
  /** Schema transaction to endorse */
  txn?: TransactionRecord;
}

export interface UpdateConnectionRequest {
  /**
   * Optional alias to apply to connection for later use
   * @example "Bob, providing quotes"
   */
  alias?: string;
}

export interface UpdateContactRequest {
  /**
   * The new email to associate with this tenant.
   * @example "example@exampleserver.com"
   */
  contact_email?: string;
}

export interface UpdateKeyRequest {
  /**
   * New kid to bind to the key pair, such as a verificationMethod.
   * @example "did:web:example.com#key-02"
   */
  kid: string;
  /**
   * Multikey of the key pair to update
   * @example "z6MkgKA7yrw5kYSiDuQFcye4bMaJpcfHFry3Bx45pdWh3s8i"
   */
  multikey: string;
}

export interface UpdateKeyResponse {
  /**
   * The associated kid
   * @example "did:web:example.com#key-02"
   */
  kid?: string;
  /**
   * The Public Key Multibase format (multikey)
   * @example "z6MkgKA7yrw5kYSiDuQFcye4bMaJpcfHFry3Bx45pdWh3s8i"
   */
  multikey?: string;
}

export interface UpdateProfileSettings {
  /**
   * Agent config key-value pairs
   * @example {"ACAPY_INVITE_PUBLIC":true,"log-level":"INFO","public-invites":false}
   */
  extra_settings?: Record<string, any>;
}

export interface UpdateWalletRequest {
  /** Agent config key-value pairs */
  extra_settings?: Record<string, any>;
  /**
   * Image url for this wallet. This image url is publicized (self-attested) to other agents as part of forming a connection.
   * @example "https://aries.ca/images/sample.png"
   */
  image_url?: string;
  /**
   * Label for this wallet. This label is publicized (self-attested) to other agents as part of forming a connection.
   * @example "Alice"
   */
  label?: string;
  /**
   * Webhook target dispatch type for this wallet. default: Dispatch only to webhooks associated with this wallet. base: Dispatch only to webhooks associated with the base wallet. both: Dispatch to both webhook targets.
   * @example "default"
   */
  wallet_dispatch_type?: 'default' | 'both' | 'base';
  /** List of Webhook URLs associated with this subwallet */
  wallet_webhook_urls?: string[];
}

export type UpgradeResult = object;

export interface V10CredentialBoundOfferRequest {
  /** Optional counter-proposal */
  counter_proposal?: CredentialProposal;
}

export interface V10CredentialConnFreeOfferRequest {
  /** Whether to respond automatically to credential requests, creating and issuing requested credentials */
  auto_issue?: boolean;
  /** Whether to remove the credential exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /** Human-readable comment */
  comment?: string | null;
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id: string;
  credential_preview: CredentialPreview;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
}

export interface V10CredentialCreate {
  /** Whether to remove the credential exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /** Human-readable comment */
  comment?: string | null;
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id?: string;
  credential_proposal: CredentialPreview;
  /**
   * Credential issuer DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  issuer_did?: string;
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id?: string;
  /**
   * Schema issuer DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  schema_issuer_did?: string;
  /**
   * Schema name
   * @example "preferences"
   */
  schema_name?: string;
  /**
   * Schema version
   * @pattern ^[0-9.]+$
   * @example "1.0"
   */
  schema_version?: string;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
}

export interface V10CredentialExchange {
  /**
   * Issuer choice to issue to request in this credential exchange
   * @example false
   */
  auto_issue?: boolean;
  /**
   * Holder choice to accept offer in this credential exchange
   * @example false
   */
  auto_offer?: boolean;
  /**
   * Issuer choice to remove this credential exchange record when complete
   * @example false
   */
  auto_remove?: boolean;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id?: string;
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /** Credential as stored */
  credential?: IndyCredInfo;
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  credential_definition_id?: string;
  /**
   * Credential exchange identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  credential_exchange_id?: string;
  /**
   * Credential identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  credential_id?: string;
  /** (Indy) credential offer */
  credential_offer?: IndyCredAbstract;
  /** Credential offer message */
  credential_offer_dict?: CredentialOffer;
  /** Credential proposal message */
  credential_proposal_dict?: CredentialProposal;
  /** (Indy) credential request */
  credential_request?: IndyCredRequest;
  /** (Indy) credential request metadata */
  credential_request_metadata?: Record<string, any>;
  /**
   * Error message
   * @example "Credential definition identifier is not set in proposal"
   */
  error_msg?: string;
  /**
   * Issue-credential exchange initiator: self or external
   * @example "self"
   */
  initiator?: 'self' | 'external';
  /**
   * Parent thread identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  parent_thread_id?: string;
  /** Credential as received, prior to storage in holder wallet */
  raw_credential?: IndyCredential;
  /** Revocation registry identifier */
  revoc_reg_id?: string;
  /** Credential identifier within revocation registry */
  revocation_id?: string;
  /**
   * Issue-credential exchange role: holder or issuer
   * @example "issuer"
   */
  role?: 'holder' | 'issuer';
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id?: string;
  /**
   * Issue-credential exchange state
   * @example "credential_acked"
   */
  state?: string;
  /**
   * Thread identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  thread_id?: string;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface V10CredentialExchangeAutoRemoveRequest {
  /** Whether to remove the credential exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
}

export interface V10CredentialExchangeListResult {
  /** Aries#0036 v1.0 credential exchange records */
  results?: V10CredentialExchange[];
}

export interface V10CredentialFreeOfferRequest {
  /** Whether to respond automatically to credential requests, creating and issuing requested credentials */
  auto_issue?: boolean;
  /** Whether to remove the credential exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /** Human-readable comment */
  comment?: string | null;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id: string;
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id: string;
  credential_preview: CredentialPreview;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
}

export interface V10CredentialIssueRequest {
  /** Human-readable comment */
  comment?: string | null;
}

export interface V10CredentialProblemReportRequest {
  description: string;
}

export interface V10CredentialProposalRequestMand {
  /** Whether to remove the credential exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /** Human-readable comment */
  comment?: string | null;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id: string;
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id?: string;
  credential_proposal: CredentialPreview;
  /**
   * Credential issuer DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  issuer_did?: string;
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id?: string;
  /**
   * Schema issuer DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  schema_issuer_did?: string;
  /**
   * Schema name
   * @example "preferences"
   */
  schema_name?: string;
  /**
   * Schema version
   * @pattern ^[0-9.]+$
   * @example "1.0"
   */
  schema_version?: string;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
}

export interface V10CredentialProposalRequestOpt {
  /** Whether to remove the credential exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /** Human-readable comment */
  comment?: string | null;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id: string;
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id?: string;
  credential_proposal?: CredentialPreview;
  /**
   * Credential issuer DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  issuer_did?: string;
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id?: string;
  /**
   * Schema issuer DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  schema_issuer_did?: string;
  /**
   * Schema name
   * @example "preferences"
   */
  schema_name?: string;
  /**
   * Schema version
   * @pattern ^[0-9.]+$
   * @example "1.0"
   */
  schema_version?: string;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
}

export interface V10CredentialStoreRequest {
  credential_id?: string;
}

export interface V10DiscoveryExchangeListResult {
  results?: V10DiscoveryRecord[];
}

export interface V10DiscoveryRecord {
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id?: string;
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /** Disclose message */
  disclose?: Disclose;
  /**
   * Credential exchange identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  discovery_exchange_id?: string;
  /** Query message */
  query_msg?: Query;
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Thread identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  thread_id?: string;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export type V10PresentProofModuleResponse = object;

export interface V10PresentationCreateRequestRequest {
  /** Whether to remove the presentation exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /**
   * Verifier choice to auto-verify proof presentation
   * @example false
   */
  auto_verify?: boolean;
  comment?: string | null;
  proof_request: IndyProofRequest;
  /**
   * Whether to trace event (default false)
   * @example false
   */
  trace?: boolean;
}

export interface V10PresentationExchange {
  /**
   * Prover choice to auto-present proof as verifier requests
   * @example false
   */
  auto_present?: boolean;
  /**
   * Verifier choice to remove this presentation exchange record when complete
   * @example false
   */
  auto_remove?: boolean;
  /** Verifier choice to auto-verify proof presentation */
  auto_verify?: boolean;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id?: string;
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Error message
   * @example "Invalid structure"
   */
  error_msg?: string;
  /**
   * Present-proof exchange initiator: self or external
   * @example "self"
   */
  initiator?: 'self' | 'external';
  /** (Indy) presentation (also known as proof) */
  presentation?: IndyProof;
  /**
   * Presentation exchange identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  presentation_exchange_id?: string;
  /** Presentation proposal message */
  presentation_proposal_dict?: PresentationProposal;
  /** (Indy) presentation request (also known as proof request) */
  presentation_request?: IndyProofRequest;
  /** Presentation request message */
  presentation_request_dict?: PresentationRequest;
  /**
   * Present-proof exchange role: prover or verifier
   * @example "prover"
   */
  role?: 'prover' | 'verifier';
  /**
   * Present-proof exchange state
   * @example "verified"
   */
  state?: string;
  /**
   * Thread identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  thread_id?: string;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
  /**
   * Whether presentation is verified: true or false
   * @example "true"
   */
  verified?: 'true' | 'false';
  verified_msgs?: string[];
}

export interface V10PresentationExchangeList {
  /** Aries RFC 37 v1.0 presentation exchange records */
  results?: V10PresentationExchange[];
}

export interface V10PresentationProblemReportRequest {
  description: string;
}

export interface V10PresentationProposalRequest {
  /** Whether to respond automatically to presentation requests, building and presenting requested proof */
  auto_present?: boolean;
  /** Whether to remove the presentation exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /** Human-readable comment */
  comment?: string | null;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id: string;
  presentation_proposal: IndyPresPreview;
  /**
   * Whether to trace event (default false)
   * @example false
   */
  trace?: boolean;
}

export interface V10PresentationSendRequest {
  /** Whether to remove the presentation exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /** Nested object mapping proof request attribute referents to requested-attribute specifiers */
  requested_attributes: Record<string, IndyRequestedCredsRequestedAttr>;
  /** Nested object mapping proof request predicate referents to requested-predicate specifiers */
  requested_predicates: Record<string, IndyRequestedCredsRequestedPred>;
  /** Self-attested attributes to build into proof */
  self_attested_attributes: Record<string, string>;
  /**
   * Whether to trace event (default false)
   * @example false
   */
  trace?: boolean;
}

export interface V10PresentationSendRequestRequest {
  /** Whether to remove the presentation exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /**
   * Verifier choice to auto-verify proof presentation
   * @example false
   */
  auto_verify?: boolean;
  comment?: string | null;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id: string;
  proof_request: IndyProofRequest;
  /**
   * Whether to trace event (default false)
   * @example false
   */
  trace?: boolean;
}

export interface V10PresentationSendRequestToProposal {
  /** Whether to remove the presentation exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /**
   * Verifier choice to auto-verify proof presentation
   * @example false
   */
  auto_verify?: boolean;
  /**
   * Whether to trace event (default false)
   * @example false
   */
  trace?: boolean;
}

export interface V20CredAttrSpec {
  /**
   * MIME type: omit for (null) default
   * @example "image/jpeg"
   */
  'mime-type'?: string | null;
  /**
   * Attribute name
   * @example "favourite_drink"
   */
  name: string;
  /**
   * Attribute value: base64-encode if MIME type is present
   * @example "martini"
   */
  value: string;
}

export interface V20CredBoundOfferRequest {
  /** Optional content for counter-proposal */
  counter_preview?: V20CredPreview;
  /** Credential specification criteria by format */
  filter?: V20CredFilter;
}

export interface V20CredExFree {
  /** Whether to remove the credential exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /** Human-readable comment */
  comment?: string | null;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id: string;
  credential_preview?: V20CredPreview;
  /** Credential specification criteria by format */
  filter: V20CredFilter;
  /**
   * Optional identifier used to manage credential replacement
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  replacement_id?: string | null;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
  /** For ld-proofs. Verification method for signing. */
  verification_method?: string | null;
}

export interface V20CredExRecord {
  /**
   * Issuer choice to issue to request in this credential exchange
   * @example false
   */
  auto_issue?: boolean;
  /**
   * Holder choice to accept offer in this credential exchange
   * @example false
   */
  auto_offer?: boolean;
  /**
   * Issuer choice to remove this credential exchange record when complete
   * @example false
   */
  auto_remove?: boolean;
  /** Attachment content by format for proposal, offer, request, and issue */
  by_format?: V20CredExRecordByFormat;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id?: string;
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Credential exchange identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_ex_id?: string;
  /** Serialized credential issue message */
  cred_issue?: V20CredIssue;
  /** Credential offer message */
  cred_offer?: V20CredOffer;
  /** Credential preview from credential proposal */
  cred_preview?: V20CredPreview;
  /** Credential proposal message */
  cred_proposal?: V20CredProposal;
  /** Serialized credential request message */
  cred_request?: V20CredRequest;
  /**
   * Error message
   * @example "The front fell off"
   */
  error_msg?: string;
  /**
   * Issue-credential exchange initiator: self or external
   * @example "self"
   */
  initiator?: 'self' | 'external';
  /**
   * Parent thread identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  parent_thread_id?: string;
  /**
   * Issue-credential exchange role: holder or issuer
   * @example "issuer"
   */
  role?: 'issuer' | 'holder';
  /**
   * Issue-credential exchange state
   * @example "done"
   */
  state?:
    | 'proposal-sent'
    | 'proposal-received'
    | 'offer-sent'
    | 'offer-received'
    | 'request-sent'
    | 'request-received'
    | 'credential-issued'
    | 'credential-received'
    | 'done'
    | 'credential-revoked'
    | 'abandoned'
    | 'deleted';
  /**
   * Thread identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  thread_id?: string;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface V20CredExRecordAnonCreds {
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_ex_anoncreds_id?: string;
  /**
   * Corresponding v2.0 credential exchange record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_ex_id?: string;
  /**
   * Credential identifier stored in wallet
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_id_stored?: string;
  /** Credential request metadata for anoncreds holder */
  cred_request_metadata?: Record<string, any>;
  /**
   * Credential revocation identifier within revocation registry
   * @example "did:(method):3:CL:20:tag"
   */
  cred_rev_id?: string;
  /**
   * Revocation registry identifier
   * @example "did:(method):4:did:<method>:3:CL:20:tag:CL_ACCUM:0"
   */
  rev_reg_id?: string;
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface V20CredExRecordByFormat {
  cred_issue?: Record<string, any>;
  cred_offer?: Record<string, any>;
  cred_proposal?: Record<string, any>;
  cred_request?: Record<string, any>;
}

export interface V20CredExRecordDetail {
  anoncreds?: V20CredExRecordAnonCreds;
  /** Credential exchange record */
  cred_ex_record?: V20CredExRecord;
  indy?: V20CredExRecordIndy;
  ld_proof?: V20CredExRecordLDProof;
  vc_di?: V20CredExRecord;
}

export interface V20CredExRecordIndy {
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Corresponding v2.0 credential exchange record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_ex_id?: string;
  /**
   * Record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_ex_indy_id?: string;
  /**
   * Credential identifier stored in wallet
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_id_stored?: string;
  /** Credential request metadata for indy holder */
  cred_request_metadata?: Record<string, any>;
  /**
   * Credential revocation identifier within revocation registry
   * @pattern ^[1-9][0-9]*$
   * @example "12345"
   */
  cred_rev_id?: string;
  /**
   * Revocation registry identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):4:([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+))(:.+)?:CL_ACCUM:(.+$)
   * @example "WgWxqztrNooG92RXvxSTWv:4:WgWxqztrNooG92RXvxSTWv:3:CL:20:tag:CL_ACCUM:0"
   */
  rev_reg_id?: string;
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface V20CredExRecordLDProof {
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Corresponding v2.0 credential exchange record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_ex_id?: string;
  /**
   * Record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_ex_ld_proof_id?: string;
  /**
   * Credential identifier stored in wallet
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  cred_id_stored?: string;
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface V20CredExRecordListResult {
  /** Credential exchange records and corresponding detail records */
  results?: V20CredExRecordDetail[];
}

export interface V20CredFilter {
  /** Credential filter for anoncreds */
  anoncreds?: V20CredFilterAnonCreds;
  /** Credential filter for indy */
  indy?: V20CredFilterIndy;
  /** Credential filter for linked data proof */
  ld_proof?: LDProofVCDetail;
  /** Credential filter for vc_di */
  vc_di?: V20CredFilterVCDI;
}

export interface V20CredFilterAnonCreds {
  /**
   * Credential definition identifier
   * @example "did:(method):3:CL:20:tag"
   */
  cred_def_id?: string;
  /**
   * Credential issuer ID
   * @example "did:(method):WgWxqztrNooG92RXvxSTWv"
   */
  issuer_id?: string;
  /**
   * Schema identifier
   * @example "did:(method):2:schema_name:1.0"
   */
  schema_id?: string;
  /**
   * Schema issuer ID
   * @example "did:(method):WgWxqztrNooG92RXvxSTWv"
   */
  schema_issuer_id?: string;
  /**
   * Schema name
   * @example "preferences"
   */
  schema_name?: string;
  /**
   * Schema version
   * @example "1.0"
   */
  schema_version?: string;
}

export interface V20CredFilterIndy {
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id?: string;
  /**
   * Credential issuer DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  issuer_did?: string;
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id?: string;
  /**
   * Schema issuer DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  schema_issuer_did?: string;
  /**
   * Schema name
   * @example "preferences"
   */
  schema_name?: string;
  /**
   * Schema version
   * @pattern ^[0-9.]+$
   * @example "1.0"
   */
  schema_version?: string;
}

export interface V20CredFilterLDProof {
  /** Credential filter for linked data proof */
  ld_proof: LDProofVCDetail;
}

export interface V20CredFilterVCDI {
  /**
   * Credential definition identifier
   * @pattern ^([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}):3:CL:(([1-9][0-9]*)|([123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+)):(.+)?$
   * @example "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag"
   */
  cred_def_id?: string;
  /**
   * Credential issuer DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  issuer_did?: string;
  /**
   * Schema identifier
   * @pattern ^[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}:2:.+:[0-9.]+$
   * @example "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0"
   */
  schema_id?: string;
  /**
   * Schema issuer DID
   * @pattern ^(did:(sov|indy):)?[123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz]{21,22}$
   * @example "did:indy:sovrin:WRfXPg8dantKVubE3HX8pw"
   */
  schema_issuer_did?: string;
  /**
   * Schema name
   * @example "preferences"
   */
  schema_name?: string;
  /**
   * Schema version
   * @pattern ^[0-9.]+$
   * @example "1.0"
   */
  schema_version?: string;
}

export interface V20CredFormat {
  /**
   * Attachment identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  attach_id: string;
  /**
   * Attachment format specifier
   * @example "aries/ld-proof-vc-detail@v1.0"
   */
  format: string;
}

export interface V20CredIssue {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /** Human-readable comment */
  comment?: string | null;
  /** Credential attachments */
  'credentials~attach': AttachDecorator[];
  /** Acceptable attachment formats */
  formats: V20CredFormat[];
  /**
   * Issuer-unique identifier to coordinate credential replacement
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  replacement_id?: string;
}

export interface V20CredIssueProblemReportRequest {
  description: string;
}

export interface V20CredIssueRequest {
  /** Human-readable comment */
  comment?: string | null;
}

export interface V20CredOffer {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /** Human-readable comment */
  comment?: string | null;
  credential_preview?: V20CredPreview;
  /** Acceptable credential formats */
  formats: V20CredFormat[];
  /** Offer attachments */
  'offers~attach': AttachDecorator[];
  /**
   * Issuer-unique identifier to coordinate credential replacement
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  replacement_id?: string;
}

export interface V20CredOfferConnFreeRequest {
  /** Whether to respond automatically to credential requests, creating and issuing requested credentials */
  auto_issue?: boolean;
  /** Whether to remove the credential exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /** Human-readable comment */
  comment?: string | null;
  credential_preview?: V20CredPreview;
  /** Credential specification criteria by format */
  filter: V20CredFilter;
  /**
   * Optional identifier used to manage credential replacement
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  replacement_id?: string | null;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
}

export interface V20CredOfferRequest {
  /** Whether to respond automatically to credential requests, creating and issuing requested credentials */
  auto_issue?: boolean;
  /** Whether to remove the credential exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /** Human-readable comment */
  comment?: string | null;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id: string;
  credential_preview?: V20CredPreview;
  /** Credential specification criteria by format */
  filter: V20CredFilter;
  /**
   * Optional identifier used to manage credential replacement
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  replacement_id?: string | null;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
}

export interface V20CredPreview {
  /**
   * Message type identifier
   * @example "issue-credential/2.0/credential-preview"
   */
  '@type'?: string;
  attributes: V20CredAttrSpec[];
}

export interface V20CredProposal {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /** Human-readable comment */
  comment?: string | null;
  /** Credential preview */
  credential_preview?: V20CredPreview;
  /** Credential filter per acceptable format on corresponding identifier */
  'filters~attach': AttachDecorator[];
  /** Attachment formats */
  formats: V20CredFormat[];
}

export interface V20CredRequest {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /** Human-readable comment */
  comment?: string | null;
  /** Acceptable attachment formats */
  formats: V20CredFormat[];
  /** Request attachments */
  'requests~attach': AttachDecorator[];
}

export interface V20CredRequestFree {
  /** Whether to remove the credential exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /** Human-readable comment */
  comment?: string | null;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id: string;
  /** Credential specification criteria by format */
  filter: V20CredFilterLDProof;
  /**
   * Holder DID to substitute for the credentialSubject.id
   * @example "did:key:ahsdkjahsdkjhaskjdhakjshdkajhsdkjahs"
   */
  holder_did?: string | null;
  /**
   * Whether to trace event (default false)
   * @example false
   */
  trace?: boolean;
}

export interface V20CredRequestRequest {
  /** Whether to remove the credential exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /**
   * Holder DID to substitute for the credentialSubject.id
   * @example "did:key:ahsdkjahsdkjhaskjdhakjshdkajhsdkjahs"
   */
  holder_did?: string | null;
}

export interface V20CredStoreRequest {
  credential_id?: string;
}

export interface V20DiscoveryExchangeListResult {
  results?: V20DiscoveryRecord[];
}

export interface V20DiscoveryExchangeResult {
  /** Discover Features v2.0 exchange record */
  results?: V20DiscoveryRecord;
}

export interface V20DiscoveryRecord {
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id?: string;
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /** Disclosures message */
  disclosures?: Disclosures;
  /**
   * Credential exchange identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  discovery_exchange_id?: string;
  /** Queries message */
  queries_msg?: Queries;
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Thread identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  thread_id?: string;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
}

export interface V20IssueCredSchemaCore {
  /** Whether to remove the credential exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /** Human-readable comment */
  comment?: string | null;
  credential_preview?: V20CredPreview;
  /** Credential specification criteria by format */
  filter: V20CredFilter;
  /**
   * Optional identifier used to manage credential replacement
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  replacement_id?: string | null;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
}

export type V20IssueCredentialModuleResponse = object;

export interface V20Pres {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /** Human-readable comment */
  comment?: string | null;
  /** Acceptable attachment formats */
  formats: V20PresFormat[];
  'presentations~attach': AttachDecorator[];
}

export interface V20PresCreateRequestRequest {
  /** Whether to remove the presentation exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /**
   * Verifier choice to auto-verify proof presentation
   * @example false
   */
  auto_verify?: boolean;
  comment?: string | null;
  presentation_request: V20PresRequestByFormat;
  /**
   * Whether to trace event (default false)
   * @example false
   */
  trace?: boolean;
}

export interface V20PresExRecord {
  /**
   * Prover choice to auto-present proof as verifier requests
   * @example false
   */
  auto_present?: boolean;
  /**
   * Verifier choice to remove this presentation exchange record when complete
   * @example false
   */
  auto_remove?: boolean;
  /** Verifier choice to auto-verify proof presentation */
  auto_verify?: boolean;
  /** Attachment content by format for proposal, request, and presentation */
  by_format?: V20PresExRecordByFormat;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id?: string;
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /**
   * Error message
   * @example "Invalid structure"
   */
  error_msg?: string;
  /**
   * Present-proof exchange initiator: self or external
   * @example "self"
   */
  initiator?: 'self' | 'external';
  /** Presentation message */
  pres?: V20Pres;
  /**
   * Presentation exchange identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  pres_ex_id?: string;
  /** Presentation proposal message */
  pres_proposal?: V20PresProposal;
  /** Presentation request message */
  pres_request?: V20PresRequest;
  /**
   * Present-proof exchange role: prover or verifier
   * @example "prover"
   */
  role?: 'prover' | 'verifier';
  /** Present-proof exchange state */
  state?:
    | 'proposal-sent'
    | 'proposal-received'
    | 'request-sent'
    | 'request-received'
    | 'presentation-sent'
    | 'presentation-received'
    | 'done'
    | 'abandoned'
    | 'deleted';
  /**
   * Thread identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  thread_id?: string;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
  /**
   * Whether presentation is verified: 'true' or 'false'
   * @example "true"
   */
  verified?: 'true' | 'false';
  verified_msgs?: string[];
}

export interface V20PresExRecordByFormat {
  pres?: Record<string, any>;
  pres_proposal?: Record<string, any>;
  pres_request?: Record<string, any>;
}

export interface V20PresExRecordList {
  /** Presentation exchange records */
  results?: V20PresExRecord[];
}

export interface V20PresFormat {
  /**
   * Attachment identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  attach_id: string;
  /**
   * Attachment format specifier
   * @example "dif/presentation-exchange/submission@v1.0"
   */
  format: string;
}

export interface V20PresProblemReportRequest {
  description: string;
}

export interface V20PresProposal {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /** Human-readable comment */
  comment?: string;
  /** Acceptable attachment formats */
  formats: V20PresFormat[];
  /** Attachment per acceptable format on corresponding identifier */
  'proposals~attach': AttachDecorator[];
}

export interface V20PresProposalByFormat {
  /** Presentation proposal for anoncreds */
  anoncreds?: AnonCredsPresentationRequest;
  /** Presentation proposal for DIF */
  dif?: DIFProofProposal;
  /** Presentation proposal for indy */
  indy?: IndyProofRequest;
}

export interface V20PresProposalRequest {
  /** Whether to respond automatically to presentation requests, building and presenting requested proof */
  auto_present?: boolean;
  /** Whether to remove the presentation exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /** Human-readable comment */
  comment?: string | null;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id: string;
  presentation_proposal: V20PresProposalByFormat;
  /**
   * Whether to trace event (default false)
   * @example false
   */
  trace?: boolean;
}

export interface V20PresRequest {
  /**
   * Message identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  '@id'?: string;
  /**
   * Message type
   * @example "https://didcomm.org/my-family/1.0/my-message-type"
   */
  '@type'?: string;
  /** Human-readable comment */
  comment?: string;
  /** Acceptable attachment formats */
  formats: V20PresFormat[];
  /** Attachment per acceptable format on corresponding identifier */
  'request_presentations~attach': AttachDecorator[];
  /** Whether verifier will send confirmation ack */
  will_confirm?: boolean;
}

export interface V20PresRequestByFormat {
  /** Presentation proposal for anoncreds */
  anoncreds?: AnonCredsPresentationRequest;
  /** Presentation request for DIF */
  dif?: DIFProofRequest;
  /** Presentation request for indy */
  indy?: IndyProofRequest;
}

export interface V20PresSendRequestRequest {
  /** Whether to remove the presentation exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /**
   * Verifier choice to auto-verify proof presentation
   * @example false
   */
  auto_verify?: boolean;
  comment?: string | null;
  /**
   * Connection identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  connection_id: string;
  presentation_request: V20PresRequestByFormat;
  /**
   * Whether to trace event (default false)
   * @example false
   */
  trace?: boolean;
}

export interface V20PresSpecByFormatRequest {
  /** Presentation specification for anoncreds */
  anoncreds?: AnonCredsPresSpec;
  /** Whether to remove the presentation exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /** Optional Presentation specification for DIF, overrides the PresentationExchange record's PresRequest */
  dif?: DIFPresSpec;
  /** Presentation specification for indy */
  indy?: IndyPresSpec;
  /** Record trace information, based on agent configuration */
  trace?: boolean;
}

export type V20PresentProofModuleResponse = object;

export interface V20PresentationSendRequestToProposal {
  /** Whether to remove the presentation exchange record on completion (overrides --preserve-exchange-records configuration setting) */
  auto_remove?: boolean;
  /**
   * Verifier choice to auto-verify proof presentation
   * @example false
   */
  auto_verify?: boolean;
  /**
   * Whether to trace event (default false)
   * @example false
   */
  trace?: boolean;
}

export interface VCRecord {
  contexts?: string[];
  cred_tags?: Record<string, string>;
  /** (JSON-serializable) credential value */
  cred_value?: Record<string, any>;
  expanded_types?: string[];
  /**
   * Credential identifier
   * @example "http://example.edu/credentials/3732"
   */
  given_id?: string;
  /**
   * Issuer identifier
   * @example "https://example.edu/issuers/14"
   */
  issuer_id?: string;
  proof_types?: string[];
  /**
   * Record identifier
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  record_id?: string;
  schema_ids?: string[];
  subject_ids?: string[];
}

export interface VCRecordList {
  results?: VCRecord[];
}

export interface VerifiableCredential {
  /**
   * The JSON-LD context of the credential
   * @example ["https://www.w3.org/2018/credentials/v1","https://www.w3.org/2018/credentials/examples/v1"]
   */
  '@context': any[];
  /** @example {"id":"https://example.com/credentials/status/3#94567","statusListCredential":"https://example.com/credentials/status/3","statusListIndex":"94567","statusPurpose":"revocation","type":"BitstringStatusListEntry"} */
  credentialStatus?: any;
  /** @example {"alumniOf":{"id":"did:example:c276e12ec21ebfeb1f712ebc6f1"},"id":"did:example:ebfeb1f712ebc6f1c276e12ec21"} */
  credentialSubject: any;
  /**
   * The expiration date
   * @pattern ^([0-9]{4})-([0-9]{2})-([0-9]{2})([Tt ]([0-9]{2}):([0-9]{2}):([0-9]{2})(\.[0-9]+)?)?(([Zz]|([+-])([0-9]{2}):([0-9]{2})))?$
   * @example "2010-01-01T19:23:24Z"
   */
  expirationDate?: string;
  /**
   * The ID of the credential
   * @pattern \w+:(\/?\/?)[^\s]+
   * @example "http://example.edu/credentials/1872"
   */
  id?: string;
  /**
   * The issuance date
   * @pattern ^([0-9]{4})-([0-9]{2})-([0-9]{2})([Tt ]([0-9]{2}):([0-9]{2}):([0-9]{2})(\.[0-9]+)?)?(([Zz]|([+-])([0-9]{2}):([0-9]{2})))?$
   * @example "2010-01-01T19:23:24Z"
   */
  issuanceDate?: string;
  /**
   * The JSON-LD Verifiable Credential Issuer. Either string of object with id field.
   * @example "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
   */
  issuer: any;
  /**
   * The proof of the credential
   * @example {"created":"2019-12-11T03:50:55","jws":"eyJhbGciOiAiRWREU0EiLCAiYjY0IjogZmFsc2UsICJjcml0JiNjQiXX0..lKJU0Df_keblRKhZAS9Qq6zybm-HqUXNVZ8vgEPNTAjQKBhQDxvXNo7nvtUBb_Eq1Ch6YBKY5qBQ","proofPurpose":"assertionMethod","type":"Ed25519Signature2018","verificationMethod":"did:key:z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL#z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL"}
   */
  proof: LinkedDataProof;
  /**
   * The JSON-LD type of the credential
   * @example ["VerifiableCredential","AlumniCredential"]
   */
  type: string[];
  /**
   * The valid from date
   * @pattern ^([0-9]{4})-([0-9]{2})-([0-9]{2})([Tt ]([0-9]{2}):([0-9]{2}):([0-9]{2})(\.[0-9]+)?)?(([Zz]|([+-])([0-9]{2}):([0-9]{2})))?$
   * @example "2010-01-01T19:23:24Z"
   */
  validFrom?: string;
  /**
   * The valid until date
   * @pattern ^([0-9]{4})-([0-9]{2})-([0-9]{2})([Tt ]([0-9]{2}):([0-9]{2}):([0-9]{2})(\.[0-9]+)?)?(([Zz]|([+-])([0-9]{2}):([0-9]{2})))?$
   * @example "2010-01-01T19:23:24Z"
   */
  validUntil?: string;
  [key: string]: any;
}

export interface VerifiablePresentation {
  /**
   * The JSON-LD context of the presentation
   * @example ["https://www.w3.org/2018/credentials/v1"]
   */
  '@context': any[];
  /**
   * The JSON-LD Verifiable Credential Holder. Either string of object with id field.
   * @example "did:key:z6MkpTHR8VNsBxYAAWHut2Geadd9jSwuBV8xRoAnwWsdvktH"
   */
  holder?: any;
  /**
   * The ID of the presentation
   * @pattern \w+:(\/?\/?)[^\s]+
   * @example "http://example.edu/presentations/1872"
   */
  id?: string;
  /**
   * The proof of the presentation
   * @example {"created":"2019-12-11T03:50:55","jws":"eyJhbGciOiAiRWREU0EiLCAiYjY0IjogZmFsc2UsICJjcml0JiNjQiXX0..lKJU0Df_keblRKhZAS9Qq6zybm-HqUXNVZ8vgEPNTAjQKBhQDxvXNo7nvtUBb_Eq1Ch6YBKY5qBQ","proofPurpose":"assertionMethod","type":"Ed25519Signature2018","verificationMethod":"did:key:z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL#z6Mkgg342Ycpuk263R9d8Aq6MUaxPn1DDeHyGo38EefXmgDL"}
   */
  proof: LinkedDataProof;
  /**
   * The JSON-LD type of the presentation
   * @example ["VerifiablePresentation"]
   */
  type: string[];
  verifiableCredential?: Record<string, any>[];
  [key: string]: any;
}

export interface VerifyCredentialRequest {
  options?: LDProofVCOptions;
  verifiableCredential?: VerifiableCredential;
}

export interface VerifyCredentialResponse {
  results?: PresentationVerificationResult;
}

export interface VerifyDiRequest {
  /** @example {"hello":"world","proof":[{"cryptosuite":"eddsa-jcs-2022","proofPurpose":"assertionMethod","type":"DataIntegrityProof","verificationMethod":"did:key:                            z6MksxraKwH8GR7NKeQ4HVZAeRKvD76kfd6G7jm8MscbDmy8#                                z6MksxraKwH8GR7NKeQ4HVZAeRKvD76kfd6G7jm8MscbDmy8","proofValue":"zHtda8vV7kJQUPfSKiTGSQDhZfhkgtpnVziT7cdEzhu                            fjPjbeRmysHvizMJEox1eHR7xUGzNUj1V4yaKiLw7UA6E"}]} */
  securedDocument: Record<string, any>;
}

export interface VerifyDiResponse {
  /**
   * Verified
   * @example true
   */
  verified?: boolean;
}

export interface VerifyPresentationRequest {
  options?: LDProofVCOptions;
  verifiablePresentation?: VerifiablePresentation;
}

export interface VerifyPresentationResponse {
  results?: PresentationVerificationResult;
}

export interface VerifyRequest {
  /** Signed document */
  doc: SignedDoc;
  /** Verkey to use for doc verification */
  verkey?: string;
}

export interface VerifyResponse {
  /** Error text */
  error?: string;
  valid: boolean;
}

export interface W3CCredentialsListRequest {
  contexts?: string[];
  /** Given credential id to match */
  given_id?: string;
  /** Credential issuer identifier to match */
  issuer_id?: string;
  /** Maximum number of results to return */
  max_results?: number;
  proof_types?: string[];
  /** Schema identifiers, all of which to match */
  schema_ids?: string[];
  /** Subject identifiers, all of which to match */
  subject_ids?: string[];
  /** Tag filter */
  tag_query?: Record<string, string>;
  types?: string[];
}

export interface WalletList {
  /** List of wallet records */
  results?: WalletRecord[];
}

export type WalletModuleResponse = object;

export interface WalletRecord {
  /**
   * Time of record creation
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  created_at?: string;
  /** Mode regarding management of wallet key */
  key_management_mode: 'managed' | 'unmanaged';
  /** Settings for this wallet. */
  settings?: Record<string, any>;
  /**
   * Current record state
   * @example "active"
   */
  state?: string;
  /**
   * Time of last record update
   * @pattern ^\d{4}-\d\d-\d\d[T ]\d\d:\d\d(?:\:(?:\d\d(?:\.\d{1,6})?))?(?:[+-]\d\d:?\d\d|Z|)$
   * @example "2021-12-31T23:59:59Z"
   */
  updated_at?: string;
  /**
   * Wallet record ID
   * @example "3fa85f64-5717-4562-b3fc-2c963f66afa6"
   */
  wallet_id: string;
}

export interface WebvhAddVM {
  /**
   * An user provided verification method ID
   * @example "key-01"
   */
  id?: string;
  /**
   * An existing multikey to bind.
   * @example ""
   */
  multikey?: string;
  relationships?: (
    | 'keyAgreement'
    | 'authentication'
    | 'assertionMethod'
    | 'capabilityInvocation'
    | 'capabilityDelegation'
  )[];
  type?: 'Multikey' | 'JsonWebKey';
}

export interface WebvhCreate {
  options?: CreateOptions;
}

export interface WebvhCreateWitnessInvitation {
  /**
   * Optional alias for the connection.
   * @example "Issuer 01"
   */
  alias?: string;
  /**
   * Optional label for the connection recipient.
   * @example "Witnessing Service"
   */
  label?: string;
}

export interface WebvhDeactivate {
  /**
   * ID of the DID to deactivate
   * @example "did:webvh:scid:example.com:prod:1"
   */
  id: string;
}

export interface WebvhUpdateWhois {
  presentation: Presentation;
}

export interface WriteLedger {
  ledger_id?: string;
}
