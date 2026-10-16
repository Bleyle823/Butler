# Request for recognition and support

**To:** Web3 Clubs Kenya

**From:** [Name], Bachelor of Business Information Technology (BBIT), Class of 2024, Africa Nazarene University; Web3 Clubs member

**Date:** [Date]

**Contact:** [Email] · [Phone]

**Subject:** Letter of recognition for Butler — a hotel robot paid when the job is done

Dear Web3 Clubs,

I am a member of Web3 Clubs. I come to the lab from time to time for the sessions and the talks. I am writing from inside the club to ask for **only a short letter of recognition** stating that **Butler** is a project by a member: a hospitality humanoid that carries out a hotel delivery job and leaves a **public, checkable record** that the work happened and that settlement followed the proof. The letter should be one I can share with the hackathon programme organisers at **Canteen** (**arjun@thecanteenapp.com**). Please issue it on club letterhead from an **official email** with **arjun@thecanteenapp.com copied**.

**Butler** is a physical-AI build for Kenyan hospitality. In the demonstration, **servebot-1**—a mobile manipulator with an arm and gripper, modelled on a PAL TIAGo service robot—works in a simulated hotel kitchen: a guest orders food or a drink, the robot collects it at the counter, carries it to the guest floor, and sets it down. That is the job hotels repeat every day. What makes Butler a Web3 project is what happens beside the arm.

**peaq** gives the robot a public machine identity and writes **pickup** and **delivery** to an open work record when those moments occur, so a guest, a hotel, or a partner who was not in the corridor can still verify which machine did the job.

**Circle** is the payments and custody layer. Butler uses **Circle developer-controlled wallets** so the guest, the robot, the kitchen counter, and the operator each have a wallet Circle can sign for programmatically—without putting Circle’s entity secret or signing keys on the robot or in the Webots controller. A small local **settler** service holds those secrets and calls Circle when telemetry says pickup or delivery happened. That is how a machine becomes a **payer** (paying the kitchen at pickup from the robot wallet) and a **payee** (receiving a share when escrow releases), while custody stays with infrastructure a hotel operator can reason about, not with firmware on the arm.

**Arc** is the settlement chain. On Arc Testnet in the demo, value moves in **USDC**—digital dollars—through a **programmable escrow** contract: the guest’s funds are locked before the robot starts, then released in a defined split when delivery is proved. Arc is built so **USDC is both the payment and the gas**: the robot wallet settles in dollars without a separate volatile token for fees, which matters for a service robot that must keep a small operating balance above each transfer. peaq answers *who did the work and when*; Circle and Arc answer *who held the dollars, who got paid, and under what rule*.

Keys stay off the robot; the settler signs for Circle and peaq the way production fleets keep payment logic off the device.

In Kenya this pattern is useful because hospitality is already a major employer and a major export story—hundreds of accredited hotels, tens of thousands of rooms, and a tourism sector that supports well over a million jobs—while much of the work inside a property is still learned by watching someone carry a tray. Travellers book on a phone; operators are under pressure to show digital service without losing trust at the door. Butler does not ask a guest to learn a wallet to order a drink in the demo; it shows that **when a humanoid (or any service robot) finishes a repeatable hotel task, dollars can wait for proof, pay the kitchen when the item leaves the counter, and split the rest when the tray arrives**, with **peaq** as the durable receipt and **Arc / USDC** as the settlement rail. That is a classroom-sized story today and a pilot-sized story tomorrow if a willing hotel agrees.

The first building is a hotel. The same rule—pay when the work is proved—can later cover other repeated tasks in that building and in others. Today the hotel is a computer simulation; the onchain machine identity, the written pickup and delivery events, and a test kitchen payment on Arc are already real on test networks.

## Why the record matters

Kenya's hotels are a large workplace. More than 900 accredited hotels and more than 45,000 rooms already exist, inside a tourism sector that earned about KSh 0.5 trillion in 2025 and supported about 1.8 million travel and tourism jobs. A guest, a hotel, and the maker of a robot should be able to check that a delivery happened, and that the money moved because of it.

In February 2026, Tourism and Wildlife Cabinet Secretary Rebecca Miano said technology of this kind should send income to the people who actually do the work, with less leakage along the way. Butler is a small version of that remark: the kitchen is paid when the item is picked up, and the rest moves when the item is on the table. This letter is my own request.

The aims are a demo a non-technical guest can follow, a record that names the robot, and a path from this simulation to a willing hotel. The letter stays with those aims.

## What the demo holds

1. **Identity.** The robot, servebot-1, has a public identity on peaq. A job belongs to that machine.
2. **Money that waits (Circle on Arc).** **Circle** provisions and signs **developer-controlled wallets** for the guest, robot, kitchen, and operator; the settler—not the robot—holds custody and triggers transfers. **Arc** (testnet in the demo) settles in **USDC**: guest funds lock in **escrow** before motion, pickup pays vending from the robot wallet, delivery releases the remainder to operator, maker, and robot reserve. A real hotel guest would still pay in ordinary money; wallets sit with the demonstration.
3. **Proof.** Pickup and delivery are written to the public record when they happen. A pickup and a delivery are already written. A test payment to the kitchen counter has gone through. The guest's full hold, from lock to release, is still being completed on the test network.
4. **The arm stays in charge of the arm.** The robot runs the delivery. A payment problem holds the next order. The record does not drive the robot.

## Why this is a Web3 project

Butler is a hotel service whose payment and work record can be checked by someone who was not in the corridor. That is the Web3 use: a job with a public receipt. The product is the delivery. The lab sessions are the right place to test whether a person outside the club can follow it.

I already come for talks. I need help saying the four points above to a hotel manager in plain language, and a demo in front of people who will say if the story is clear.

## The demo

![Simulated hotel kitchen — servebot-1 in the Webots kitchen world](images/simulated-hotel-kitchen.jpg)

*Caption: Simulation. Where the order starts.*

![servebot-1 in the simulated hotel kitchen and dining area](images/servebot-kitchen-simulation.jpg)

*Caption: Simulation. Pickup.*

**[Image: the order on the table]**

*Caption: Simulation. The proof that releases the payment.*

<video src="videos/one-delivery-order-to-table.mp4" controls width="100%"></video>

*Caption: One simulated paid job. Label: simulation. Say on the slide which payment step is done and which is still being finished.*

## What I have already shown

The path to Butler runs through work that is already on the record.

At the National Intelligence Research University (NIRU) National AI Hackathon, together with a team of two, I built a drone project, **Maritime Anomaly System**, and took it to a podium finish.

![Presenting on stage at the NIRU National AI Hackathon](images/niru-hackathon-stage.jpg)

*Caption: Presenting the drone project on stage at the NIRU National AI Hackathon.*

![Presenting to a review panel at the NIRU National AI Hackathon](images/niru-hackathon-room.jpg)

*Caption: Presenting the drone project at the NIRU National AI Hackathon.*

In April 2026 we presented that drone project at the 3rd Mashariki Cooperation Conference in Diani, Kwale. The conference was hosted by the National Intelligence Service. Officials there included His Excellency Dr. William Samoei Ruto, C.G.H., President of the Republic of Kenya; Hon. Onesimus Kipchumba Murkomen, Cabinet Secretary for Interior and National Administration; and Mr. Noordin Mohamed Haji, Director-General of the National Intelligence Service. We presented the work to that audience.

![Presentation to Hon. Onesimus Kipchumba Murkomen and Mr. Noordin Mohamed Haji](images/presentation-murkomen-noordin.jpg)

*Caption: Presenting the project to Hon. Onesimus Kipchumba Murkomen, Cabinet Secretary for Interior and National Administration, and Mr. Noordin Mohamed Haji, Director-General of the National Intelligence Service.*

![Presentation to His Excellency Dr. William Samoei Ruto](images/presentation-ruto.jpg)

*Caption: Presenting the project to His Excellency Dr. William Samoei Ruto, C.G.H., President of the Republic of Kenya.*

I have taken **Maritime Anomaly System** to a national hackathon podium, explained it to a Cabinet-level audience, and kept showing up at the Web3 Clubs lab. Butler is the build that follows that hackathon and those presentations. A real hotel comes only with that hotel's agreement.

## What I am asking

1. A **short letter of recognition** on club letterhead, stating that Butler is a Web3 Clubs project by a member (a BBIT graduate of Africa Nazarene University, Class of 2024), for me to share with **Canteen**, the hackathon programme organisers (**arjun@thecanteenapp.com**). Please issue it from an **official email** with **arjun@thecanteenapp.com copied**.

## What the club gains

A written acknowledgement of a Kenyan hospitality build that ties a public work record to a Cabinet Secretary's public remarks on sending income to the people who do the work. The request in this letter is mine.

## Next step

A written reply, or a short call, is enough to agree the wording of the recognition letter. I can be reached at [Email] and [Phone].

Respectfully,

[Name]

Bachelor of Business Information Technology, Class of 2024

Africa Nazarene University

Web3 Clubs member

## Sources

### Kenya hospitality and policy

- Ministry of Tourism and Wildlife, press release, 2 April 2026 — about KSh 0.5 trillion in 2025 tourism earnings: [PDF (Magical Kenya)](https://magicalkenya.com/wp-content/uploads/2026/04/KENYAS-TOURISM-SECTOR-ACHIEVES-STRONG-GROWTH-IN-2025-RECORDING-Ksh.-0.5-TRILLION-IN-EARNINGS_final-1.pdf); [Ministry downloads](https://www.tourism.go.ke/downloads/).
- The Standard, 3 April 2026 — record earnings and about 7.9 million travellers (2.7M international, 5.2M domestic): [Tourism earnings hit record Sh500 billion](https://www.standardmedia.co.ke/business/article/2001544519/tourism-earnings-hit-record-sh500-billion-as-arrivals-near-8m).
- Invest Kenya — tourism sector snapshot: more than 900 accredited hotels, 45k+ rooms, 7.7% bed-capacity growth in 2024: [Tourism — InvestKenya](https://www.investkenya.go.ke/tourism/).
- World Travel and Tourism Council, 2026 Economic Impact Research — about 1.8 million travel and tourism jobs in Kenya in 2025 (~8.3% of employment): [WTTC news release](https://wttc.org/news/kenya-boosts-africas-tourism-growth-emerging-as-a-leading-sustainable-tourism-powerhouse); [Kenya EIR (Research Hub)](https://researchhub.wttc.org/product/kenya-economic-impact-report).
- The Star, 5 February 2026 — Tourism CS Rebecca Miano at the World Governments Summit (Dubai) on AI, smart data, and local communities as primary beneficiaries of the tourism value chain: [CS Miano pushes for AI tech-driven tourism](https://www.the-star.co.ke/sasa/technology/2026-02-05-cs-miano-pushes-for-ai-tech-driven-tourism). See also [Capital FM summary](https://capitalfm.africa/miano-kenya-leveraging-ai-to-lead-next-era-of-global-tourism/).

### Butler stack (peaq, Circle, Arc)

- **peaq** — machine identity and public work record (Economics 2.0 on mainnet): [Economics 2.0 (docs)](https://docs.peaq.xyz/peaqos/concepts/economics-2-0); [Machine Explorer](https://machines.peaq.xyz/economics); [servebot-1 machine page](https://machines.peaq.xyz/machine/63056357364750406110742192000069244844268702226710579694851149582072404420819) (Butler demo).
- **Circle** — developer-controlled wallets and programmatic USDC transfers (custody off the robot): [Dev-controlled wallets](https://developers.circle.com/wallets/dev-controlled); [Create a dev-controlled wallet (quickstart)](https://developers.circle.com/wallets/dev-controlled/create-your-first-wallet).
- **Arc** — Circle’s stablecoin-native L1; USDC as gas; Butler demo on Arc Testnet (chain `5042002`): [Arc chain overview](https://docs.arc.io/arc-chain); [Stablecoin-native model](https://docs.arc.io/arc/concepts/stablecoin-native-model); [USDC contract addresses](https://docs.arc.io/arc/references/contract-addresses); [Arc Testnet faucet](https://faucet.circle.com).

### Programme and community

- **Canteen** — hosts the Tameion Agents Hackathon; programme contact **arjun@thecanteenapp.com**: [About Canteen](https://thecanteenapp.com/about/); [Tameion Agents Hackathon · Canteen × Circle](https://tameion.thecanteenapp.com/); [Arc community event page](https://community.arc.io/public/events/tameion-agents-hackathon-jb1w9clwx7).
- **Web3 Clubs Kenya** — member community and Nairobi exploration lab: [web3clubs.xyz](https://web3clubs.xyz/); [LinkedIn](https://www.linkedin.com/company/web3developerclubs).
