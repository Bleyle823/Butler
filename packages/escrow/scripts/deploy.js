const { ethers } = require("hardhat");

async function main() {
  const names = [
    "ESCROW_USDC",
    "ESCROW_SETTLER",
    "ESCROW_OPERATOR",
    "ESCROW_MANUFACTURER",
    "ESCROW_RESERVE",
    "DEPLOYER_PRIVATE_KEY",
  ];
  const missing = names.filter((name) => !process.env[name]);
  if (missing.length > 0) {
    throw new Error(`Missing ${missing.join(", ")}`);
  }

  const Escrow = await ethers.getContractFactory("ButlerEscrow");
  const escrow = await Escrow.deploy(
    process.env.ESCROW_USDC,
    process.env.ESCROW_SETTLER,
    process.env.ESCROW_OPERATOR,
    process.env.ESCROW_MANUFACTURER,
    process.env.ESCROW_RESERVE,
  );
  await escrow.waitForDeployment();
  console.log("ButlerEscrow", await escrow.getAddress());
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
