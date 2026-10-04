const { expect } = require("chai");
const { ethers } = require("hardhat");

const AMOUNT = 6_000_000n;

describe("ButlerEscrow", function () {
  let usdc;
  let escrow;
  let guest;
  let settler;
  let operator;
  let manufacturer;
  let reserve;
  let jobId;
  let machineId;

  beforeEach(async function () {
    [guest, settler, operator, manufacturer, reserve] = await ethers.getSigners();
    jobId = ethers.keccak256(ethers.toUtf8Bytes("job-1"));
    machineId = ethers.keccak256(ethers.toUtf8Bytes("servebot-1"));

    const Usdc = await ethers.getContractFactory("MockUSDC");
    usdc = await Usdc.deploy();
    const Escrow = await ethers.getContractFactory("ButlerEscrow");
    escrow = await Escrow.deploy(
      await usdc.getAddress(),
      settler.address,
      operator.address,
      manufacturer.address,
      reserve.address,
    );

    await usdc.mint(guest.address, AMOUNT);
    await usdc.connect(guest).approve(await escrow.getAddress(), AMOUNT);
  });

  it("pays 80/10/10 on release", async function () {
    await escrow.connect(guest).deposit(jobId, machineId, AMOUNT);
    await escrow.connect(settler).release(jobId);

    expect(await usdc.balanceOf(operator.address)).to.equal(4_800_000n);
    expect(await usdc.balanceOf(manufacturer.address)).to.equal(600_000n);
    expect(await usdc.balanceOf(reserve.address)).to.equal(600_000n);
    expect(await usdc.balanceOf(await escrow.getAddress())).to.equal(0n);
  });

  it("leaves integer dust with the operator", async function () {
    await usdc.mint(guest.address, 5);
    await usdc.connect(guest).approve(await escrow.getAddress(), 5);
    const odd = ethers.keccak256(ethers.toUtf8Bytes("odd"));

    await escrow.connect(guest).deposit(odd, machineId, 5);
    await escrow.connect(settler).release(odd);

    expect(await usdc.balanceOf(operator.address)).to.equal(5n);
    expect(await usdc.balanceOf(manufacturer.address)).to.equal(0n);
    expect(await usdc.balanceOf(reserve.address)).to.equal(0n);
  });

  it("refunds the full deposit", async function () {
    await escrow.connect(guest).deposit(jobId, machineId, AMOUNT);
    await escrow.connect(settler).refund(jobId);
    expect(await usdc.balanceOf(guest.address)).to.equal(AMOUNT);
  });

  it("rejects a non-settler and a second release or refund", async function () {
    await escrow.connect(guest).deposit(jobId, machineId, AMOUNT);

    await expect(escrow.connect(operator).release(jobId)).to.be.revertedWithCustomError(escrow, "NotSettler");

    await escrow.connect(settler).release(jobId);

    await expect(escrow.connect(settler).release(jobId)).to.be.revertedWithCustomError(escrow, "AlreadyDone");
    await expect(escrow.connect(settler).refund(jobId)).to.be.revertedWithCustomError(escrow, "AlreadyDone");
  });

  it("refuses a settler that is also the operator", async function () {
    const Escrow = await ethers.getContractFactory("ButlerEscrow");
    await expect(
      Escrow.deploy(
        await usdc.getAddress(),
        operator.address,
        operator.address,
        manufacturer.address,
        reserve.address,
      ),
    ).to.be.revertedWithCustomError(Escrow, "SettlerIsOperator");
  });
});
