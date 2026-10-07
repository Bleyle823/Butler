# Butler

This is a physical AI project: a fully autonomous hospitality robot in the Webots simulator that picks up orders , food and drinks in a hotel kitchen, delivers them , and gets paid in USDC on Circle’s Arc chain.

The robot is `servebot-1`, a TIAGo. A guest orders kitchen service. Circle locks the guest’s USDC in escrow on Arc before the robot moves. On pickup the robot pays the vending counter from its own Circle wallet. When telemetry shows the order on the table, Circle releases the escrow and peaq records the job against the robot’s machine id. There is no front desk and no invoice. The dollars move because the work happened.

On Arc, USDC is both the money and the gas, so the machine settles in dollars without a second token for fees. The arm was already automated. Arc is what lets that arm get paid when the work is proven.

## Video

_Add a recording of one full paid run here._

## Screenshots

_Kitchen world._

_servebot-1 at the counter._

_Honey jar on the table._

_Webots console with Circle and peaq lines._

## What this means for Circle and Arc

Machines can be payers and payees in USDC, not only devices that trigger a human bill.

Programmable escrow on Arc holds the guest’s money until telemetry says the job happened, then splits it.

Circle developer-controlled wallets keep custody off the robot. The Webots controller never holds Circle’s entity secret. A service, here the vending counter, can be paid by the machine mid-task.

On Arc, gas and the payment come from the same USDC balance. A robot wallet needs headroom above the transfer itself.

peaq is the public work record beside the Arc transfers, so the payment and the machine identity are both onchain.

Hospitality is the wrapper. Dollar settlement for a completed skill is the product. Other hotel tasks, then other buildings, can use the same pattern. That is a direction, not a fleet in the field.

## What shipped

- One PAL Robotics TIAGo, named `servebot-1`, in Webots R2025a
- Circle developer-controlled wallets and a Foundry escrow on Arc Testnet
- A peaq Economics 2.0 machine on peaq mainnet
- A local settler that holds the Circle secret and writes peaq the way peaq’s own robots call `peaqos_node`
- Settlement that waits for pickup and delivery proof

Operator steps live in [`docs/RUN.md`](docs/RUN.md).

## The robot

`servebot-1` is a TIAGo with a seven-joint arm and gripper. `mission_control` runs the jar tree. `butler_observe` reads the scene and posts pose, pickup, and delivery. It serves rooms 1204, 1205, and 1206 and does not drive into them. The paid set is the honey jar, jam jar 1, and jam jar 2. One job. Press Play posts that order to the settler if none is waiting.

Webots controller Python is 3.9. `peaq-os-sdk` needs 3.10 or newer, so the SDK stays in the settler. The peaq controller key stays in a local address-keyed wallet file.

## The machine

- Network: peaq mainnet, chain `3338`, Economics 2.0
- Decimal id: `63056357364750406110742192000069244844268702226710579694851149582072404420819`
- Bytes32: `0x8b68a22dc5d3c9c64f444db3928d7ee5907c829a8e4419dbcc04d1103c9aa8d3`
- Controller: `0x4360d54AdB797bf75013870de1AAD152839587D0`
- EventRegistry: `0xA1e7F1d7B24dAb55Dc92491e6d9B89F6E925Ad1e`
- Activation: `0x406ed5c4f889cb9cd0c9aa940223f3144ddeb2a16b3f95c55bb8a8a7ce443e6c`
- Page: https://machines.peaq.xyz/machine/63056357364750406110742192000069244844268702226710579694851149582072404420819
- DID image: https://files.catbox.moe/ec4zej.png

## The money

- Chain: Arc Testnet `5042002`. Explorer: https://testnet.arcscan.app
- USDC: `0x3600000000000000000000000000000000000000`
- Escrow: `0xeEFF543d9312fAc816c0C8b0f37ddB4545bBBdaD`
- Guest: `0x566c7344100b046e467eae9d1efb8bd5abf646a2`
- Robot: `0x9a8709845445661fd9b044bc907e38faf6d27168`
- Vending: `0x01ed2f186edab0b28dd796afe0762fac5a5b092d`
- Operator: `0x0fa08f931a9d4430f614ab5c49f095bf0ae2240d`
- Manufacturer: `0xC26ce44fC41BB13503d20945653767abcbd17f7E`
- Settler: `0x2838270efa7a1aa0196bb98a8f8230771aed3b80`

The guest locks 6.00 USDC before the robot starts. Pickup of the honey jar pays vending 2.00 from the robot wallet. Delivery of that jar releases escrow as 4.80 to the operator, 0.60 to the manufacturer, and 0.60 to the robot reserve. peaq records 200 cents on pickup and 600 cents on delivery. The two jam jars finish the same job.

## A finished run

Job `0xdccdc144afa9ac17fdc72e44127b2e788734b3b38740f5b3d1ae7d347b77ff46`.

| Step | Circle id | Arc |
| --- | --- | --- |
| Deposit 6.00 | `f150bf2e-53e4-5c01-ba07-4476f92ad54d` | No Arc hash. Circle state `FAILED` (`INSUFFICIENT_TOKEN`). |
| Vending 2.00 | `82652451-d1a6-5bc3-81fb-30903cf5f92e` | [0x513091d549e7aac239a502781b73400e5d183f1dd78921ede314c60f6308ed43](https://testnet.arcscan.app/tx/0x513091d549e7aac239a502781b73400e5d183f1dd78921ede314c60f6308ed43) |
| Release | `4f4753ee-ee8c-5134-8d15-930c1afb1e70` | No Arc hash. Circle state `FAILED` (`ESTIMATION_ERROR`). |

peaq pickup: [0x7131f9366ff7c0516c8b8c911cf74090a6bb7ae7e1c5b296a433d537f434f21a](https://peaq.subscan.io/tx/0x7131f9366ff7c0516c8b8c911cf74090a6bb7ae7e1c5b296a433d537f434f21a)

peaq delivery: [0x629c774c2d85a390e4fcf2b4889582ec2d37ecdd7934d2c34f31043537e923d0](https://peaq.subscan.io/tx/0x629c774c2d85a390e4fcf2b4889582ec2d37ecdd7934d2c34f31043537e923d0)

## How it is wired

Play, or the hotel page, posts `/order` to the settler at `http://127.0.0.1:8788`. The settler talks to Circle, then posts the paid goal to the bridge at `http://127.0.0.1:8787`. The robot reads that goal and runs the tree. `butler_observe` posts telemetry. Pickup and delivery go back to the settler, which pays on Arc and writes peaq. Keys stay out of git.

## Endorsements

_Add quotes here._

## Partnerships

_Add partners here._

## Traction

_Add numbers, venues, and follow-on work here._
