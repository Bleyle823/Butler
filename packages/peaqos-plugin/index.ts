import type { IntegrationPlugin } from "../registry";
import { registerIntegration } from "../registry";
import { PeaqosIcon } from "./icon";

const peaqosPlugin: IntegrationPlugin = {
  type: "peaqos",
  egress: "fixed-host",
  label: "peaqOS",
  description:
    "Economics 2.0 reads and controller writes (Record Revenue, renew, suspend) on peaq mainnet",
  icon: PeaqosIcon,
  formFields: [
    {
      id: "mcrUrl",
      label: "MCR API URL",
      type: "url",
      placeholder: "https://mcr.peaq.xyz",
      configKey: "mcrUrl",
      envVar: "PEAQOS_MCR_URL",
      helpText: "Public MCR host. Defaults to https://mcr.peaq.xyz",
    },
    {
      id: "verifyUrl",
      label: "Verify API URL",
      type: "url",
      placeholder: "https://mcr.peaq.xyz",
      configKey: "verifyUrl",
      envVar: "PEAQOS_VERIFY_API_URL",
      helpText: "Public Verify host. Mainnet only.",
    },
    {
      id: "rpcUrl",
      label: "peaq RPC URL",
      type: "url",
      placeholder: "https://quicknode1.peaq.xyz",
      configKey: "rpcUrl",
      envVar: "PEAQOS_RPC_URL",
      helpText: "Mainnet HTTP RPC. Used for subscription and owner/controller reads. Contract writes use chain 3338.",
    },
  ],
  testConfig: {
    getTestFunction: async () => {
      const { testPeaqos } = await import("./test");
      return testPeaqos;
    },
  },
  actions: [
    {
      slug: "get-credit-rating",
      label: "Get Credit Rating",
      description: "GET MCR for did:peaq:{id}",
      category: "peaqOS",
      stepFunction: "getCreditRatingStep",
      stepImportPath: "get-credit-rating",
      outputFields: [
        { field: "success", description: "Whether the read succeeded" },
        { field: "rating", description: "Letter rating if present" },
        { field: "score", description: "Numeric score if present" },
        { field: "body", description: "Raw JSON" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        {
          key: "machineId",
          label: "Machine Id or DID",
          type: "template-input",
          required: true,
        },
      ],
    },
    {
      slug: "get-machine-profile",
      label: "Get Machine Profile",
      description: "GET /machine/{did} from the MCR host",
      category: "peaqOS",
      stepFunction: "getMachineProfileStep",
      stepImportPath: "get-machine-profile",
      outputFields: [
        { field: "success", description: "Whether the read succeeded" },
        { field: "body", description: "Raw JSON" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        {
          key: "machineId",
          label: "Machine Id or DID",
          type: "template-input",
          required: true,
        },
      ],
    },
    {
      slug: "get-operator-fleet",
      label: "Get Operator Fleet",
      description: "GET /operator/{did}/machines",
      category: "peaqOS",
      stepFunction: "getOperatorFleetStep",
      stepImportPath: "get-operator-fleet",
      outputFields: [
        { field: "success", description: "Whether the read succeeded" },
        { field: "body", description: "Raw JSON" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        {
          key: "operatorDid",
          label: "Operator DID",
          type: "template-input",
          required: true,
        },
      ],
    },
    {
      slug: "get-verification",
      label: "Get Verification",
      description: "GET /v1/verify/machines/{machineId}. unverified is normal without a chip.",
      category: "peaqOS",
      stepFunction: "getVerificationStep",
      stepImportPath: "get-verification",
      outputFields: [
        { field: "success", description: "Whether the read succeeded" },
        { field: "chipStatus", description: "unverified, verified, expired, or revoked" },
        { field: "kybStatus", description: "KYB status" },
        { field: "body", description: "Raw JSON" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        {
          key: "machineId",
          label: "Machine Id",
          type: "template-input",
          required: true,
        },
      ],
    },
    {
      slug: "get-subscription-state",
      label: "Get Subscription State",
      description: "Read MachineSubscription for Active / Grace / lapsed",
      category: "peaqOS",
      stepFunction: "getSubscriptionStateStep",
      stepImportPath: "get-subscription-state",
      outputFields: [
        { field: "success", description: "Whether the read succeeded" },
        { field: "eligible", description: "Active or Grace" },
        { field: "body", description: "Raw JSON" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        {
          key: "machineId",
          label: "Machine Id",
          type: "template-input",
          required: true,
        },
      ],
    },
    {
      slug: "get-owner-and-controller",
      label: "Get Owner and Controller",
      description: "Read MachineRegistry ownerOf and controllerOf",
      category: "peaqOS",
      stepFunction: "getOwnerAndControllerStep",
      stepImportPath: "get-owner-and-controller",
      outputFields: [
        { field: "success", description: "Whether the read succeeded" },
        { field: "owner", description: "Owner address" },
        { field: "controller", description: "Controller address" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        {
          key: "machineId",
          label: "Machine Id",
          type: "template-input",
          required: true,
        },
      ],
    },
    {
      slug: "record-revenue",
      label: "Record Revenue",
      description: "submitEvent type 0 as controller. Butler: sourceChainId 0, trustLevel 0, Arc hash in rawData.",
      category: "peaqOS",
      stepFunction: "recordRevenueStep",
      stepImportPath: "record-revenue",
      outputFields: [
        { field: "success", description: "Whether the tx was sent" },
        { field: "transactionHash", description: "peaq tx hash" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        { key: "machineId", label: "Machine Id", type: "template-input", required: true },
        { key: "value", label: "Value (cents)", type: "template-input", placeholder: "600", required: true },
        { key: "currency", label: "Currency", type: "template-input", placeholder: "USD" },
        { key: "sourceChainId", label: "Source Chain Id", type: "template-input", placeholder: "0" },
        { key: "trustLevel", label: "Trust Level", type: "template-input", placeholder: "0" },
        { key: "sourceTxHash", label: "Source Tx Hash", type: "template-input", placeholder: "0x..." },
        { key: "rawData", label: "Raw Data", type: "template-textarea", placeholder: "arc:0x..." },
      ],
    },
    {
      slug: "record-activity",
      label: "Record Activity",
      description: "submitEvent type 1 as controller. currency must be empty.",
      category: "peaqOS",
      stepFunction: "recordActivityStep",
      stepImportPath: "record-activity",
      outputFields: [
        { field: "success", description: "Whether the tx was sent" },
        { field: "transactionHash", description: "peaq tx hash" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        { key: "machineId", label: "Machine Id", type: "template-input", required: true },
        { key: "value", label: "Value", type: "template-input", placeholder: "1" },
        { key: "rawData", label: "Raw Data", type: "template-textarea" },
      ],
    },
    {
      slug: "renew-subscription",
      label: "Renew Subscription",
      description: "Renew the machine subscription as controller",
      category: "peaqOS",
      stepFunction: "renewSubscriptionStep",
      stepImportPath: "renew-subscription",
      outputFields: [
        { field: "success", description: "Whether the tx was sent" },
        { field: "transactionHash", description: "peaq tx hash" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        { key: "machineId", label: "Machine Id", type: "template-input", required: true },
      ],
    },
    {
      slug: "suspend-machine",
      label: "Suspend Machine",
      description: "Suspend the machine as controller",
      category: "peaqOS",
      stepFunction: "suspendMachineStep",
      stepImportPath: "suspend-machine",
      outputFields: [
        { field: "success", description: "Whether the tx was sent" },
        { field: "transactionHash", description: "peaq tx hash" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        { key: "machineId", label: "Machine Id", type: "template-input", required: true },
      ],
    },
    {
      slug: "resume-machine",
      label: "Resume Machine",
      description: "Resume the machine as controller",
      category: "peaqOS",
      stepFunction: "resumeMachineStep",
      stepImportPath: "resume-machine",
      outputFields: [
        { field: "success", description: "Whether the tx was sent" },
        { field: "transactionHash", description: "peaq tx hash" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        { key: "machineId", label: "Machine Id", type: "template-input", required: true },
      ],
    },
  ],
};

registerIntegration(peaqosPlugin);
export default peaqosPlugin;
