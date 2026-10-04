require("@nomicfoundation/hardhat-toolbox");

const deployerKey = process.env.DEPLOYER_PRIVATE_KEY;

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.24",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  paths: {
    sources: "./src",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
  },
  networks: {
    arc_testnet: {
      url: "https://rpc.testnet.arc.io",
      chainId: 5042002,
      accounts: deployerKey ? [deployerKey] : [],
    },
  },
};
