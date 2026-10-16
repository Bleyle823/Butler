# Butler
## The Robot That Gets Paid When the Work Is Done

**A pay-per-skill hospitality robot with onchain identity, verified delivery, and autonomous USDC settlement**

> *Hackathon: Tameion Agents Hackathon — Canteen × Circle*
> *Builder: Bleyle Osewe · Bennybleylle09@gmail.com · 0705297628*
> *Community: Web3 Clubs Kenya*
> *Stack: peaq · Circle · Arc · Webots*

---

---

## ▸ COVER ILLUSTRATION

```
[ FULL-WIDTH BANNER IMAGE ]
Hotel corridor. Humanoid robot mid-roll, tray in hand.
Overlaid: a transaction hash. A delivery confirmed.
Tag: "servebot-1 — paid on delivery."
```

---

---

# PART I — THE PROJECT

---

## 1. What Butler Is

Butler is a hotel service robot with a financial layer built in.

A guest orders food or a drink. The robot collects it from the kitchen counter and leaves it at the room. The guest's USDC is held in escrow the moment the order is placed. It releases only after delivery is confirmed onchain. The robot has a public identity on the peaq network — so the job names a machine, not a person, not a company, not a vague promise.

No invoice is raised. No manager is buzzed. No spreadsheet is updated by hand. The robot delivered and got paid. The receipt is public.

That is the whole thing. Simple to say. Hard to build. Worth building.

---

## 2. The Problem It Solves

**For the guest:** there is no way to know if what was promised was delivered, or where the money went.

**For the hotel:** tipping, labour disputes, and opaque payment trails sit between the kitchen and the room every shift.

**For the robot maker or RaaS operator:** leasing robots at a flat monthly fee means you earn the same whether the robot ran one delivery or a hundred. Premium skills — speed, precision, fragile cargo — are invisible in the invoice.

**For the sector:** Kenya's hospitality industry runs roughly KSh 0.5 trillion in annual tourism earnings (2025, Ministry of Tourism and Wildlife) across more than 900 accredited hotels and 45,000+ rooms, supporting approximately 1.8 million travel and tourism jobs (WTTC, 2026 Economic Impact Research). That is a large, high-volume, high-frequency delivery environment. The financial infrastructure underneath it — how money moves from guest to kitchen to staff to operator — is almost entirely manual.

Butler is a working answer to that gap.

---

## 3. Why Now

In February 2026, Tourism and Wildlife Cabinet Secretary Rebecca Miano, speaking at the World Governments Summit in Dubai, said AI technology in tourism should send income to the people who actually do the work, with less leakage along the way.

Separately: peaqOS — the machine identity and settlement layer Butler is built on — went live in LG's CLOiSim environment in 2026, powering the first live demonstration of robots that transact, monetize skills, and coordinate services autonomously on a pay-per-skill basis. That demo runs in a simulated hotel. Butler runs in a simulated hotel. The infrastructure that LG used in that demonstration is the same infrastructure Butler is already wired to.

The moment is not theoretical. The stack exists. The hardware category exists. The policy conversation is happening. What is missing is an implementation built for the Kenyan hospitality market — and a team ready to take it from simulation to a willing hotel.

---

## 3A. Physical AI — The Field Today and Where It Is Going

**Physical AI** (also called embodied AI) is AI that perceives, reasons, and acts in the real world — on a factory floor, in a warehouse, or in a hotel corridor. It is not a chat window. It is a machine that moves, senses, and completes tasks.

### Where the market stands (2025–2026)

Market definitions vary, but the direction is consistent: rapid growth and heavy capital flowing into robots plus foundation models.

| Segment | Approx. size / trajectory | Notes |
|--------|---------------------------|--------|
| Embodied AI (software + systems) | ~$4.4B (2025) → ~$23B (2030), ~39% CAGR | MarketsandMarkets; robots segment fastest-growing |
| Humanoid robots | ~$2.1–2.4B (2025) → ~$4.2B (2026); ~$38–40B by 2033–2035 | Grand View Research; Emergen Research |
| Physical AI (broader robotics + AI) | ~$33B (2025) → ~$42B (2026) → ~$294B (2034) | Fortune Business Insights |
| Hospitality service robots | ~$0.61B (2025) → ~$0.76B (2026) → ~$2.23B (2031) | Mordor Intelligence |

**Installed base and deployment:** The International Federation of Robotics cites roughly **4.66 million industrial robots** operating worldwide (2024). In hospitality alone, industry analyses cite **20,000+ service robot units** deployed across hotels, restaurants, and healthcare globally, with **delivery robots accounting for ~40% of hospitality-robot revenue** in 2025. In China, hotel service-robot penetration reportedly **exceeded 30% in 2025**, with further growth expected — a signal of how fast delivery automation can scale once economics and ops fit.

**What is actually working in hotels:** Operators consistently prioritise **high-frequency, repetitive, low-ambiguity tasks** — room delivery, transport, restocking, guidance — not full replacement of guest-facing emotional labour. Taiwan’s largest hotel operator (Dunqian / CHECK inn) reports **up to ~200 robot deliveries per day on weekends** on delivery-focused deployments, with strong success rates on those tasks. That is the same task class Butler models: kitchen → room, with a verifiable handoff.

### The inflection (why 2026 feels different)

1. **Foundation models for robots** — NVIDIA GR00T, Google Gemini Robotics, Figure Helix, and startups such as Physical Intelligence and Skild AI are racing to own general-purpose control and simulation stacks. Jensen Huang has described early 2026 as a **“ChatGPT moment” for physical AI**: the models are catching up to the hardware.

2. **Simulation-to-deployment pipeline** — Digital twins and simulators (including LG CLOiSim, Isaac, Webots-class environments) let teams prove dispatch, telemetry, and settlement before touching a live floor.

3. **Machines as economic actors** — Identity, escrow, and pay-per-task settlement (peaqOS, Circle Arc, agent wallets) turn each completed delivery into a **settled economic event**, not a log line in a PMS.

4. **Labour and service pressure** — Persistent staffing gaps in hospitality and tourism (Kenya: ~1.8M travel and tourism jobs; global operators cite cost and consistency as adoption drivers) push automation where ROI is measurable.

### Where physical AI is likely to go (2027–2035)

```
[ ILLUSTRATION: Timeline — Simulation → Pilot venues → Fleet pay-per-skill → Multi-site agent dispatch ]
```

- **Short term:** Delivery, cleaning, and back-of-house robots with human escalation; payment and audit trails become as important as navigation.
- **Medium term:** Fleet orchestration (which robot, which skill, which price), premium skills monetised per task, not per lease month — the model LG/peaq demonstrated in CLOiSim.
- **Long term:** Cross-venue machine credit, collateral, and underwriting built on telemetry + settlement history; robots and agents paying one another for sub-tasks (APIs, charging, spare parts) on stablecoin rails.

Butler sits at the **earliest monetisable wedge**: one robot, one hotel workflow, one USDC escrow, one public receipt — in simulation today, in a Nairobi lab and pilot hotel next.

---

## 4. The Demo

Butler currently runs in a Webots simulation. The world is a hotel. The robot is called **servebot-1**.

---

### 4.1 Simulation — Where the Order Starts

```
[ IMAGE PLACEHOLDER ]
Caption: The hotel-ui order screen.
A guest selects their room (1204, 1205, or 1206) and taps "Order the drinks."
The settler records the job. The bridge locks the USDC.
```

---

### 4.2 Simulation — Robot Specs and Description

```
[ ROBOT DESCRIPTION AND SPEC SHEET PLACEHOLDER ]

Robot name: servebot-1
Platform: TIAGo humanoid (Webots R2025a)
Controller: mission_control (Python 3.9 / ROS 2)
Arm: [spec]
Gripper: [spec]
Navigation: [spec]
Sensor suite: [spec]
Payload: heineken beer · beverage can · water bottle
peaq identity: [Machine NFT address]
```

---

### 4.3 Simulation — Robot in Action

```
[ IMAGE/VIDEO PLACEHOLDER ]
Caption: servebot-1 at the kitchen counter. Pickup event recorded on peaq.

[ IMAGE/VIDEO PLACEHOLDER ]
Caption: servebot-1 en route to the room. Arm carrying the tray.

[ IMAGE/VIDEO PLACEHOLDER ]
Caption: Delivery confirmed. USDC released. Transaction hash visible.
```

---

### 4.4 What the Demo Proves

| Step | What happens | Who can verify |
|------|-------------|----------------|
| Order placed | Job posted to settler, USDC locked on bridge | Guest, hotel, anyone |
| Pickup | Robot takes the order from kitchen counter | peaq record, public |
| Delivery | Robot places order at room door | peaq record, public |
| Settlement | USDC released to operator, maker, robot reserve | Circle / Arc explorer |
| Escalation | Payment failure blocks next order | Automatic, no human needed |

One complete business workflow, run by the agent from start to finish: receive revenue → assess liquidity → pay the obligation (kitchen) → record the decision → release the balance on verified delivery.

---

## 5. The Stack

```
[ ARCHITECTURE DIAGRAM PLACEHOLDER ]

Guest UI (hotel-ui · port 3001)
  └─▶ Settler (packages/settler · port 8788)
        ├─▶ Circle dev-controlled wallets (USDC escrow · Arc Testnet 5042002)
        ├─▶ peaq mainnet (servebot-1 identity · job record)
        └─▶ Webots simulation (mission_control controller)
              └─▶ Bridge (packages/bridge · port 8787)
                    └─▶ butler_observe (pickup / delivery events)
```

### Infrastructure choices and why

**peaq network** — machine identity and public work record. peaq's Economics 2.0 gives every robot a decentralised ID, a Machine NFT for onchain ownership, and an immutable delivery audit trail. servebot-1 is already registered. The job names that machine. [machines.peaq.xyz/machine/63056357364750…94851149582072404420819]

**Circle developer-controlled wallets** — programmatic USDC; custody sits with the settler, not the robot. The guest's funds are locked on placement and released on delivery confirmation. Pickup triggers a payment to the kitchen from the robot's own balance. [developers.circle.com/wallets/dev-controlled]

**Arc** — Circle's stablecoin-native L1; USDC is the gas token. The Butler demo runs on Arc Testnet (chain ID 5042002). A pickup event and a delivery event have already been recorded. A test payment to the kitchen counter has cleared. [docs.arc.io/arc-chain]

**Webots R2025a** — the simulation environment. The TIAGo robot, the kitchen, and three guest rooms (1204, 1205, 1206) are all modelled. The simulation is the current working environment; the physics and the delivery logic are production-grade.

---

## 5A. Why Arc Matters — Opportunity and Volume for the Network

Circle launched **Arc mainnet** (September 2026) as an open, EVM-compatible L1 **purpose-built for programmable money, real-time settlement, and agentic economic activity** — with USDC as native gas, sub-second deterministic finality, and deep integration into Circle’s platform (USDC, Gateway, Payments Network, StableFX, Agent Stack).

For **Arc as a network**, Butler is not a cosmetic demo. It is a **repeatable, high-frequency settlement pattern** aligned with what Circle is explicitly building for:

| Arc strategic theme | What Butler generates on-chain |
|--------------------|--------------------------------|
| **Agentic commerce** | Settler acts as the financial agent: hold USDC, pay kitchen on pickup, release on delivery, block on policy failure |
| **USDC-native fees** | Every escrow lock, transfer, and split pays predictable USDC-denominated network fees — no volatile gas token |
| **Job escrow & settlement** | Maps to ERC-8183-style job lifecycles (create → fund → verify → settle) described in Arc’s agentic-economy docs |
| **Machine-to-service payments** | Robot identity on peaq + payment rail on Arc = work attestation linked to money movement |
| **Real-world volume narrative** | Hospitality = many small, frequent settlements — the opposite of one-off whale transfers |

### Network scale (why volume matters)

Public explorer analytics (indexed chain data, not estimates) illustrate Arc’s throughput appetite:

- **~48M+ transactions in a recent 30-day window**; **~1.1M+ daily transactions** (Arc Explorer analytics)
- **Launch-day peak: ~7.76M transactions** (16 September 2026)
- **USDC as gas and settlement** — fees paid in USDC; average fee per transaction on the order of **fractions of a cent** in recent periods

Circle’s own positioning: agents are already executing trades, routing liquidity, and settling in **USDC**; Arc is described as the **first chain designed from genesis for this participant class**. USDC reportedly accounts for the overwhelming share of agent-driven transaction volume in Circle’s agent-payment flows.

### Volume Butler can bring to Arc (illustrative)

These are **scenario models** for investors and ecosystem partners — not promises. They show why a hospitality pilot in Kenya can matter for **transaction count and USDC velocity**, not just brand.

| Scenario | Deliveries / week (all robots) | USDC settlement events / week (min.) | Notes |
|----------|-------------------------------|----------------------------------------|--------|
| Web3 Clubs pilot | 50 | 150+ | Lock + kitchen pay + release per job |
| 3 Nairobi hotels, 2 robots each | 600 | 1,800+ | Weekday-heavy; weekends higher |
| 30 hotels, 100 robots (scale) | 10,000 | 30,000+ | Approaches “always-on agent treasury” territory |

Each delivery is at least **three Arc-relevant movements** (guest escrow, kitchen payment, final split). Add retries, refunds, and fleet top-ups and the **event count multiplies**. Arc wins when Butler wins: **more USDC settled, more agent-policy enforcement, more proof that sub-dollar machine commerce is real.**

```
[ ILLUSTRATION: Flow diagram ]
Guest USDC → Arc escrow → kitchen payment (pickup) → multi-recipient release (delivery)
Caption: "Every completed room service run = multiple deterministic USDC settlements on Arc."
```

**For Circle / Tameion judges:** Butler is a **complete agent-operated business workflow** — receive, hold, pay obligation, release, log, escalate — on the same stack Arc was built to serve, with a **physical AI** story that extends agent payments beyond APIs into **embodied work**.

---

## 6. The Financial Agent Layer (Circle / Arc Alignment)

Butler's settlement layer is a direct response to the Tameion Hackathon's AI financial agent challenge.

The challenge: build an AI agent that operates the financial side of a business end to end. Receive and hold USDC. Watch cash against upcoming obligations. Decide when to pay a vendor. Move funds when needed. Stay inside predefined budgets and approval limits. Escalate to a human only when a policy threshold is hit.

Butler's answer, applied to hospitality:

| Challenge requirement | Butler implementation |
|----------------------|----------------------|
| Agent wallet holds USDC | Circle dev-controlled wallet per job, held by settler |
| Budgets enforced in contract | Escrow released only on confirmed delivery; kitchen payment on confirmed pickup |
| Liquidity monitoring | Settler checks bridge balance before accepting each order |
| Payment workflows without a human | Settler runs autonomously; no staff intervention on standard delivery |
| Decision log | Every pickup, delivery, and payment written to peaq and Circle |
| Escalation on policy threshold | Payment failure blocks the next order; alert surfaced to operator |

One complete workflow demonstrated end to end: guest pays → funds locked → robot picks up (kitchen paid) → robot delivers (balance released) → receipt recorded onchain.

---

## 7. The peaqOS / LG CLOi Precedent

In 2026, peaqOS went live inside LG's CLOiSim environment. The demo: a simulated hotel. Three LG CLOi ServeBots. A guest orders room service. OpenCLAW picks the optimal robot. The robot navigates, delivers, and receives autonomous onchain settlement via embedded Tether WDK wallets. No invoice. No manager. No spreadsheet.

Butler is built on the same infrastructure — peaqOS identity, Circle payment rails — and runs in the same category of environment: a simulated hotel with a real delivery task.

The LG demo proved the blueprint at hardware scale. Butler proves it can be built from scratch, in East Africa, by an independent team, ready for a real hotel.

---

```
[ ILLUSTRATION PLACEHOLDER ]
Side-by-side:
Left: LG CLOi ServeBot in CLOiSim hotel corridor.
Right: servebot-1 (TIAGo) in Butler's Webots kitchen.
Caption: "Same stack. Different hardware. Same principle: paid when the work is done."
```

---

---

# PART II — THE PLAN

---

## 8. Execution Roadmap

```
[ TIMELINE ILLUSTRATION PLACEHOLDER ]
Horizontal timeline: Hackathon → Pilot → Product → Scale
```

### Phase 0 — Hackathon (Now)
**Tameion Agents Hackathon · Canteen × Circle**

- Complete the Arc testnet settlement flow (guest lock → kitchen payment → delivery release)
- Demonstrate one full end-to-end workflow in simulation before the submission deadline
- Publish the transaction hash, the pickup record, and the delivery record as public proof
- Submit to the hackathon with the live demo link (hotel-ui on port 3001, landing on port 3002)

**Deliverable:** A working simulation where a non-technical person can place an order, watch the robot deliver it, and read the transaction.

---

### Phase 1 — Pilot (3–6 months post-hackathon)
**Location: Web3 Clubs Kenya Lab + Pilot Hotel**

```
[ IMAGE PLACEHOLDER ]
Caption: Web3 Clubs Kenya lab — the robotics space where the pilot will run.
[Space for lab photo and address]
```

Web3 Clubs Kenya has confirmed:
- Butler is a recognised Web3 Clubs project
- The club's lab — including its dedicated **robotics space** — is available to Butler for pilot operations
- The club is open to hosting live demo sessions in front of hotel managers and potential partners
- Support continues beyond the hackathon

**Pilot programme goals:**
1. Move from Webots simulation to physical robot hardware in the Web3 Clubs lab
2. Run the full payment flow on Arc mainnet with a real USDC deposit
3. Invite 3–5 Nairobi hotel operations managers to a live demonstration
4. Collect feedback: what does a non-technical hotel manager need to see to say yes?
5. Identify a willing pilot hotel — the robot runs one real delivery shift per week for 60 days

**Pilot hardware:**

```
[ ROBOT HARDWARE SPEC PLACEHOLDER ]
Pilot robot: [model TBD — discussions with hardware partner]
Dimensions: [spec]
Payload: [spec]
Battery life: [spec]
Navigation: [spec]
Integration with peaqOS: via peaq-os-cli 0.0.12+
Estimated cost: [spec]
```

**Pilot metrics:**
- Deliveries completed without human intervention
- Payment settlement time (order placed → USDC released)
- Guest comprehension: can a non-technical person follow what happened?
- Zero failed settlements without an error message the operator can act on

---

### Phase 2 — Product (6–18 months)
**From one hotel to a network**

- Partner with 2–3 Nairobi hotels (starting with 4-star and above; ~200 rooms each)
- Deploy physical robots with peaqOS identity registered on peaq mainnet
- Launch the hotel-facing dashboard: one screen per delivery, one line per payment
- Introduce the pay-per-skill pricing model: hotels pay per confirmed delivery, not per robot per month
- Begin fleet coordination: multiple robots, one settler, AI dispatch

**Revenue model (pay-per-skill):**

| Tier | What the hotel pays | What Butler earns |
|------|--------------------|--------------------|
| Standard delivery | 2.00 USDC per confirmed delivery | 0.40 USDC (20%) |
| Premium delivery (speed, fragile) | 4.00 USDC | 0.80 USDC |
| Fleet dispatch (3+ robots) | 1.50 USDC per delivery | 0.30 USDC + coordination fee |

*Remaining balance distributed: kitchen, operator, robot reserve, maker royalty — all onchain.*

---

### Phase 3 — Scale (18 months+)
**Kenya → East Africa → Global hospitality**

The RaaS market is projected to reach $70B by 2030 from an estimated $25B today. The pay-per-skill model — where clients pay for tasks consumed, not capacity leased — is estimated to expand the addressable market by 3x, since that is how many businesses prefer flexible pricing to fixed-term leases.

Kenya is the entry point. More than 10,000 hotels globally have already deployed robots in some capacity. The same stack — peaqOS identity, Circle/Arc settlement, pay-per-skill dispatch — applies to:

- Smart warehouses
- Autonomous delivery (last mile and in-building)
- Airports and transit hubs
- Healthcare facilities (medication delivery, specimen transport)
- Retail operations
- Industrial automation
- Smart city services

Any environment where machines execute repeated tasks, and where a verifiable receipt of that work has value, can run on this stack.

---

---

# PART III — THE INVESTOR PITCH

---

## 9. The Market

```
[ ILLUSTRATION: Market size waterfall or concentric circles ]
Global RaaS market: $25B → $70B by 2030
Pay-per-skill addressable expansion: 3x
Kenya hospitality: KSh 0.5T earnings · 900+ hotels · 45,000+ rooms · 1.8M jobs
```

**Kenya hospitality — the numbers:**

| Metric | Figure | Source |
|--------|--------|--------|
| Annual tourism earnings (2025) | ~KSh 0.5 trillion | Ministry of Tourism and Wildlife, Apr 2026 |
| International and domestic travellers | ~7.9 million | The Standard, Apr 2026 |
| Accredited hotels | 900+ | Invest Kenya |
| Total hotel rooms | 45,000+ | Invest Kenya |
| Bed capacity growth (2024) | 7.7% | Invest Kenya |
| Travel and tourism jobs | ~1.8 million (~8.3% of employment) | WTTC, 2026 |

Kenya's hotel sector is not a small experiment. It is one of the largest organised workplaces in the country. Every delivery, every room service order, every shift that ends without a receipt is a gap Butler addresses.

---

## 10. The Opportunity

**Why hospitality first:**
- High frequency, low complexity delivery tasks — ideal for robot automation
- Guests expect reliability and transparency; they already know what they ordered
- Hotel managers are measured on guest satisfaction scores, not labour efficiency alone
- The pay-per-skill model is easier to pitch than a capex robot purchase
- Kenya's tourism growth (7.7% bed capacity expansion in 2024) means new inventory is being built right now

**Why peaq + Circle + Arc:**
- peaqOS is the only infrastructure that gives a robot a public identity and an immutable delivery record simultaneously
- Circle's developer-controlled wallets allow USDC escrow without the guest needing a crypto wallet
- Arc's stablecoin-native model means USDC is the gas token — no ETH, no bridge risk, no volatility in the payment rail
- LG already validated this exact stack in a hotel simulation at commercial hardware scale
- **Arc ecosystem fit:** Butler drives **recurring USDC settlement volume** and a showcase for **agentic treasury + policy limits** in a sector (hospitality) with global robot deployment already underway

**Arc / Circle — strategic upside for the network:**

- Positions Arc as the **settlement layer for physical AI**, not only for API x402 micropayments
- Creates a **reference implementation** for Tameion-style “AI runs the money” challenges with a legible, non-technical demo (hotel guest → robot → receipt)
- Opens a path to **Kenya and East Africa** hospitality pilots — new geography for USDC-native machine commerce
- Complements Circle Agent Stack (wallets, Gateway, nanopayments) with **multi-step escrow** tied to **telemetry-verified work**

**Why now:**
- CS Rebecca Miano's February 2026 statement signals policy-level receptivity to this kind of technology in Kenyan tourism
- The Tameion hackathon is putting this on the map globally; winning or placing creates the first press moment
- The Web3 Clubs lab provides a zero-cost pilot space with a robotics-equipped facility
- servebot-1 is already registered on peaq mainnet. The infrastructure is live.

---

## 11. The Business Model

```
[ ILLUSTRATION: Revenue flow diagram ]
Guest pays USDC →
  Settler holds escrow →
    Robot picks up (kitchen paid from robot balance) →
      Robot delivers (escrow released) →
        Split: operator / maker royalty / robot reserve →
          Butler earns per-delivery fee
```

**Unit economics (pilot estimate, per delivery):**

| Item | Amount (USDC) |
|------|--------------|
| Guest payment | 6.00 |
| Kitchen (cost of goods) | 3.00 |
| Operator (hotel) | 1.20 |
| Maker royalty | 0.60 |
| Robot reserve (maintenance fund) | 0.60 |
| Butler protocol fee | 0.60 |

*All splits enforced onchain. No manual calculation. No disputes.*

**At 20 deliveries per robot per day, 5 days per week:**
- Weekly protocol revenue per robot: ~$60 USDC
- At 10 robots across 3 hotels: ~$600/week from pilot
- At 100 robots across 30 hotels (18 months): ~$6,000/week

The model scales with fleet size, not with headcount.

---

## 12. The Ask

```
[ PLACEHOLDER FOR FUNDING ASK DETAILS ]

Seed / grant ask: $[amount]
Use of funds:
  - Hardware (pilot robot): $[amount]
  - peaq mainnet registration and subscriptions: $[amount]
  - Circle and Arc production API access: $[amount]
  - Legal and compliance (Kenya): $[amount]
  - Team (6 months): $[amount]
  - Marketing and hotel partnership outreach: $[amount]

Runway: [X] months
```

---

---

# PART IV — WHY THIS TEAM

---

## 13. The Builder

**Bleyle Osewe**
Bachelor of Business Information Technology, Class of 2024
Africa Nazarene University · Web3 Clubs Kenya member
Bennybleylle09@gmail.com · 0705297628

---

### 13.1 NIRU National AI Hackathon — Podium Finish

```
[ IMAGE PLACEHOLDER ]
Caption: Presenting the drone project on stage at the NIRU National AI Hackathon.

[ IMAGE PLACEHOLDER ]
Caption: Receiving the award at the NIRU National AI Hackathon.
```

At the National Intelligence Research University (NIRU) National AI Hackathon, Bleyle led a two-person team that built **Maritime Anomaly System**, an AI drone project for maritime surveillance and anomaly detection. The project won an award and took a podium finish.

This was a **physical AI project** — not a web app, not a chatbot. A drone, a computer vision system, a real-world task. Butler is harder, and Bleyle is further along on it than most teams at this stage.

---

### 13.2 Mashariki Cooperation Conference — Presented to the President

```
[ IMAGE PLACEHOLDER ]
Caption: Presenting the Maritime Anomaly System to His Excellency Dr. William Samoei Ruto, C.G.H., President of the Republic of Kenya, at the 3rd Mashariki Cooperation Conference, Diani, Kwale, April 2026.

[ IMAGE PLACEHOLDER ]
Caption: Presenting to Hon. Onesimus Kipchumba Murkomen, Cabinet Secretary for Interior and National Administration, and Mr. Noordin Mohamed Haji, Director-General of the National Intelligence Service.
```

In April 2026, Bleyle presented the Maritime Anomaly System at the **3rd Mashariki Cooperation Conference** in Diani, Kwale — hosted by the National Intelligence Service. The audience included:

- **H.E. Dr. William Samoei Ruto, C.G.H.** — President of the Republic of Kenya
- **Hon. Onesimus Kipchumba Murkomen** — Cabinet Secretary for Interior and National Administration
- **Mr. Noordin Mohamed Haji** — Director-General of the National Intelligence Service

Presenting technical work to a national security and government audience at this level requires clarity, precision, and the ability to make a complex system legible to a non-technical room. Butler's guest-facing interface is held to the same standard.

---

### 13.3 ETH Safari and Web3 Hackathons

Bleyle has competed at hackathons organised by ETH Safari and won prizes, including the **MetaMask prize**. His GitHub shows a steady record of shipping across Web3 and AI projects. He is one of the most active builders in the Kenyan web3 space.

```
[ PLACEHOLDER: GitHub activity chart or project list ]
GitHub: [handle]
ETH Safari prize: [project name, date, prize]
Other Web3 prizes: [list]
```

---

### 13.4 Community Backing

Web3 Clubs Kenya has formally stated:

> *"Butler is a Web3 Clubs project. The club intends to offer support beyond the hackathon. The club's lab — including its dedicated robotics space — is available to Butler for pilot operations. Bleyle is the right person to carry this."*

> *"He and his two-person team took an AI drone project to a podium finish at the NIRU National AI Hackathon. He then presented that work before an audience that included the President of Kenya, the Cabinet Secretary for Interior, and the Director-General of the National Intelligence Service."*

> *"He has also built at hackathons organized by ETH Safari and won prizes there, including the MetaMask prize. Butler is a harder problem than anything he has taken on so far, and he is further along than most."*

— Web3 Clubs Kenya official letter of recognition, October 2026

**Web3 Clubs Kenya:**
Website: https://web3clubs.xyz | X: @Web3Clubs | LinkedIn: Web3Clubs

---

### 13.5 National ICT Innovation & Integration Centre (Ministry of Education, Kenya)

Bleyle is **in active communication with the Head of the National ICT Innovation & Integration Centre (NI3C), Ministry of Education, Kenya**, regarding potential institutional support for Butler — pilot space, stakeholder introductions, or alignment with national innovation programmes.

```
[ PLACEHOLDER: Letter of intent / meeting confirmation / programme logo ]
Status: Conversations ongoing; timelines depend on ministry processes.
```

Progress has been **slower than a startup timeline would prefer** — which is normal for public-sector coordination. The outlook remains **strong** for three reasons:

1. **Prior relationship:** Bleyle **interned at the National ICT Innovation & Integration Centre (NI3C)**. He understands how the centre scopes ICT innovation, integration with education, and national digital skills agendas — and how to frame Butler as workforce-relevant physical AI, not speculative crypto.
2. **Project fit:** Butler combines **robotics, simulation, and auditable digital payments** — a teachable stack for universities and TVET pathways the Ministry cares about.
3. **Pilot narrative:** A Web3 Clubs lab pilot that Ministry-aligned institutions can observe de-risks adoption for schools and hospitality training programmes.

*Until formal support is confirmed, Butler proceeds on Web3 Clubs lab capacity and private pilot conversations — without overstating government commitment.*

---

### 13.6 Africa Nazarene University — School of Education

Bleyle is also **in communication with the Head of Department, Education, at Africa Nazarene University (ANU)** — his alma mater (BBIT, Class of 2024) — to explore support for Butler as a **capstone, research, or industry-partnership** vehicle: student involvement, demo days, and ethical / operational framing for hospitality technology in Kenya.

```
[ PLACEHOLDER: ANU partnership slide / MoU draft / department letter ]
```

ANU backing would strengthen the **pilot-to-product** path: trained operators, research citations, and a credible academic anchor for hotel managers who ask “who vouches for this?”

---

### 13.7 Why This Founder Is Equipped to Carry Butler Forward

| Strength | Evidence |
|----------|----------|
| **Physical AI delivery** | NIRU National AI Hackathon podium — Maritime Anomaly System (drone + CV), not a slide deck |
| **Highest-stakes communication** | Mashariki Cooperation Conference — presented to the President, CS Interior, DG NIS |
| **Web3 execution** | ETH Safari hackathons; **MetaMask prize**; active shipping record on GitHub |
| **Public innovation institutions** | **NI3C internship** — navigation of Ministry of Education innovation structures |
| **Community + lab** | Web3 Clubs Kenya recognition; robotics space for post-hackathon pilot |
| **University pathway** | ANU Education HOD discussions for structured support |
| **Ecosystem alignment** | Butler already on **peaq mainnet** + **Circle/Arc testnet** — matches LG/peaq pay-per-skill direction |

Butler is harder than prior projects. The combination of **embodied task, settlement agent, and Kenya market access** is rare in one founder profile at this stage.

---

---

# PART V — PROOF OF WORK

---

## 14. What Is Already on the Record

| Item | Status |
|------|--------|
| servebot-1 registered on peaq mainnet | ✓ Live |
| Pickup event written to peaq | ✓ Recorded |
| Delivery event written to peaq | ✓ Recorded |
| Test payment to kitchen counter (Circle / Arc) | ✓ Cleared |
| hotel-ui order interface running on port 3001 | ✓ Running |
| Landing page running on port 3002 | ✓ Running |
| Settler (packages/settler) managing job lifecycle | ✓ Running |
| Full guest payment flow (lock → release) on Arc testnet | In progress |

**peaq explorer link:** machines.peaq.xyz/machine/63056357364750…94851149582072404420819

---

## 15. Sources

**Kenya hospitality and policy:**
- Ministry of Tourism and Wildlife, press release, 2 April 2026 — KSh 0.5 trillion in 2025 tourism earnings: magicalkenya.com
- The Standard, 3 April 2026 — record earnings; ~7.9 million travellers: standardmedia.co.ke
- Invest Kenya — 900+ accredited hotels, 45,000+ rooms, 7.7% bed-capacity growth: investkenya.go.ke
- WTTC 2026 Economic Impact Research — ~1.8 million travel and tourism jobs in Kenya: wttc.org
- The Star, 5 February 2026 — Tourism CS Rebecca Miano, World Governments Summit, Dubai: the-star.co.ke

**Butler stack:**
- peaq Economics 2.0: https://docs.peaq.xyz/peaqos/concepts/economics-2-0
- Circle dev-controlled wallets: https://developers.circle.com/wallets/dev-controlled
- Arc chain overview: https://docs.arc.io/arc-chain
- Arc testnet faucet: https://faucet.circle.com
- Arc contract addresses: https://docs.arc.io/arc/references/contract-addresses

**Programme:**
- Canteen / Tameion Agents Hackathon: https://tameion.thecanteenapp.com/
- Arc community event: community.arc.io/public/events/tameion-…nts-hackathon-jb1w9clwx7

**Physical AI and hospitality robotics:**
- MarketsandMarkets — embodied AI market forecast: marketsandmarkets.com
- Fortune Business Insights — physical AI market: fortunebusinessinsights.com
- Grand View Research — humanoid robot market: grandviewresearch.com
- Mordor Intelligence — hospitality robots market: mordorintelligence.com
- EHL Insights — hotel robots market and deployment: insights.ehl.edu/hotel-robots
- Emergen Research — Physical AI / humanoid inflection whitepaper: emergenresearch.com

**Arc and agentic commerce:**
- Circle — Arc mainnet launch: arc.io/pressroom
- Arc Explorer analytics: arcexplorer.io/analytics
- Arc docs — agentic economy: docs.arc.io/build/agentic-economy
- Circle — agentic payments on Arc: circle.com/blog

---

---

```
[ BACK COVER ILLUSTRATION ]
Butler wordmark.
"The robot that gets paid when the work is done."
peaq · Circle · Arc · Web3 Clubs Kenya
```

---

*Butler — project by Bleyle Osewe, Web3 Clubs Kenya member.*
*Document version: October 2026.*
