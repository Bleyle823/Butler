import type { IntegrationPlugin } from "../registry";
import { registerIntegration } from "../registry";
import { CircleWalletsIcon } from "./icon";

const ARC_CHAIN_IDS = ["5042002"];

const circleWalletsPlugin: IntegrationPlugin = {
  type: "circle-wallets",
  egress: "fixed-host",
  label: "Circle Wallets",
  description:
    "Developer-controlled wallets on Arc Testnet: USDC transfer, contract execution, and wait-for-tx",
  icon: CircleWalletsIcon,
  formFields: [
    {
      id: "apiKey",
      label: "Circle API Key",
      type: "password",
      placeholder: "TEST_API_KEY:...",
      configKey: "apiKey",
      envVar: "CIRCLE_API_KEY",
      helpText: "From Circle Console. ",
      helpLink: {
        text: "console.circle.com",
        url: "https://console.circle.com",
      },
    },
    {
      id: "entitySecret",
      label: "Entity Secret",
      type: "password",
      placeholder: "64-char hex",
      configKey: "entitySecret",
      envVar: "CIRCLE_ENTITY_SECRET",
      helpText:
        "32-byte hex registered in Circle Console. Never logged. Recovery file stays off this repo.",
    },
    {
      id: "env",
      label: "Environment",
      type: "text",
      placeholder: "sandbox",
      configKey: "env",
      envVar: "CIRCLE_ENV",
      helpText: "sandbox or production",
    },
  ],
  testConfig: {
    getTestFunction: async () => {
      const { testCircleWallets } = await import("./test");
      return testCircleWallets;
    },
  },
  actions: [
    {
      slug: "transfer-usdc",
      label: "Transfer USDC",
      description: "Send USDC from a developer-controlled wallet on Arc Testnet",
      category: "Circle",
      stepFunction: "transferUsdcStep",
      stepImportPath: "transfer-usdc",
      outputFields: [
        { field: "success", description: "Whether the transfer was accepted" },
        { field: "transactionId", description: "Circle transaction id" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        {
          key: "walletId",
          label: "From Wallet Id",
          type: "template-input",
          placeholder: "{{Dispatch.walletId}}",
          required: true,
        },
        {
          key: "destinationAddress",
          label: "Destination Address",
          type: "template-input",
          placeholder: "0x...",
          required: true,
        },
        {
          key: "amount",
          label: "Amount (USDC)",
          type: "template-input",
          placeholder: "2.00",
          required: true,
        },
        {
          key: "jobId",
          label: "Job Id (idempotency)",
          type: "template-input",
          placeholder: "{{Dispatch.jobId}}",
        },
      ],
    },
    {
      slug: "wait-for-transaction",
      label: "Wait for Transaction",
      description: "Poll Circle until COMPLETE or FAILED",
      category: "Circle",
      stepFunction: "waitForTransactionStep",
      stepImportPath: "wait-for-transaction",
      outputFields: [
        { field: "success", description: "Whether the tx completed" },
        { field: "state", description: "Circle state" },
        { field: "txHash", description: "On-chain hash" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        {
          key: "transactionId",
          label: "Transaction Id",
          type: "template-input",
          placeholder: "{{TransferUSDC.transactionId}}",
          required: true,
        },
      ],
    },
    {
      slug: "execute-contract",
      label: "Execute Contract",
      description: "Call a contract from a Circle wallet (escrow deposit / release / refund)",
      category: "Circle",
      stepFunction: "executeContractStep",
      stepImportPath: "execute-contract",
      outputFields: [
        { field: "success", description: "Whether the call was accepted" },
        { field: "transactionId", description: "Circle transaction id" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        {
          key: "walletId",
          label: "Wallet Id",
          type: "template-input",
          required: true,
        },
        {
          key: "contractAddress",
          label: "Contract Address",
          type: "template-input",
          placeholder: "0x...",
          required: true,
        },
        {
          key: "abiFunctionSignature",
          label: "Function Signature",
          type: "template-input",
          placeholder: "deposit(bytes32,uint256,uint256)",
          required: true,
        },
        {
          key: "abiParameters",
          label: "ABI Parameters (JSON array)",
          type: "template-textarea",
          placeholder: '["0x...", "1", "6000000"]',
          required: true,
        },
        {
          key: "jobId",
          label: "Job Id (idempotency)",
          type: "template-input",
        },
      ],
    },
    {
      slug: "get-transaction",
      label: "Get Transaction",
      description: "Read one Circle transaction",
      category: "Circle",
      stepFunction: "getTransactionStep",
      stepImportPath: "get-transaction",
      outputFields: [
        { field: "success", description: "Whether the read succeeded" },
        { field: "state", description: "Circle state" },
        { field: "txHash", description: "On-chain hash" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        {
          key: "transactionId",
          label: "Transaction Id",
          type: "template-input",
          required: true,
        },
      ],
    },
    {
      slug: "create-wallet-set",
      label: "Create Wallet Set",
      description: "Create a developer-controlled wallet set (provision once)",
      category: "Circle",
      stepFunction: "createWalletSetStep",
      stepImportPath: "create-wallet-set",
      outputFields: [
        { field: "success", description: "Whether the set was created" },
        { field: "walletSetId", description: "Wallet set id" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        {
          key: "name",
          label: "Name",
          type: "template-input",
          placeholder: "butler-demo",
          required: true,
        },
      ],
    },
    {
      slug: "create-wallet",
      label: "Create Wallet",
      description: "Create an SCA wallet on ARC-TESTNET",
      category: "Circle",
      stepFunction: "createWalletStep",
      stepImportPath: "create-wallet",
      outputFields: [
        { field: "success", description: "Whether the wallet was created" },
        { field: "walletId", description: "Circle wallet id" },
        { field: "address", description: "Arc address" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        {
          key: "walletSetId",
          label: "Wallet Set Id",
          type: "template-input",
          required: true,
        },
        {
          key: "count",
          label: "Count",
          type: "number",
          defaultValue: 1,
        },
      ],
    },
    {
      slug: "get-wallet",
      label: "Get Wallet",
      description: "Read one developer-controlled wallet",
      category: "Circle",
      stepFunction: "getWalletStep",
      stepImportPath: "get-wallet",
      outputFields: [
        { field: "success", description: "Whether the read succeeded" },
        { field: "walletId", description: "Circle wallet id" },
        { field: "address", description: "Arc address" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        {
          key: "walletId",
          label: "Wallet Id",
          type: "template-input",
          required: true,
        },
      ],
    },
    {
      slug: "get-usdc-balance",
      label: "Get USDC Balance",
      description: "Read USDC balance for a Circle wallet on Arc Testnet",
      category: "Circle",
      stepFunction: "getUsdcBalanceStep",
      stepImportPath: "get-usdc-balance",
      outputFields: [
        { field: "success", description: "Whether the read succeeded" },
        { field: "amount", description: "USDC amount as a string" },
        { field: "error", description: "Error message if failed" },
      ],
      configFields: [
        {
          key: "walletId",
          label: "Wallet Id",
          type: "template-input",
          required: true,
        },
      ],
    },
  ],
};

registerIntegration(circleWalletsPlugin);
export default circleWalletsPlugin;

void ARC_CHAIN_IDS;
