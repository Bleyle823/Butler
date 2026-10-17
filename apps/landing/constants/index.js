import {
  benefitIcon1,
  benefitIcon2,
  benefitIcon3,
  benefitIcon4,
  file02,
  homeSmile,
  plusSquare,
  searchMd,
  tiagoFleet,
  tiagoHead,
  tiagoHospitality,
  tiagoKitchen,
  tiagoPlatform,
  tiagoPortrait,
} from "../assets";

export const hotelUiUrl =
  process.env.NEXT_PUBLIC_HOTEL_UI_URL || "http://localhost:3001";

export const machineUrl =
  "https://machines.peaq.xyz/machine/63056357364750406110742192000069244844268702226710579694851149582072404420819";

export const machineId =
  "63056357364750406110742192000069244844268702226710579694851149582072404420819";

export const jobId =
  "0x59b29db1805714cf06d906b76237df8c092321ab67ccd0ba0a72f99d2a2b4780";

export const navigation = [
  { id: "0", title: "Demo", url: "#demo" },
  { id: "1", title: "Problem", url: "#features" },
  { id: "2", title: "Stack", url: "#stack" },
  { id: "3", title: "Proof", url: "#proof" },
  { id: "4", title: "Roadmap", url: "#roadmap" },
  { id: "5", title: "Builder", url: "#builder" },
  { id: "6", title: "Place order", url: hotelUiUrl, onlyMobile: true },
];

export const heroIcons = [homeSmile, file02, searchMd, plusSquare];

export const notificationImages = [tiagoHead, tiagoHospitality, tiagoKitchen];

export const partners = ["peaq", "Circle", "Arc", "Webots", "Web3 Clubs Kenya"];

export const specLines = [
  "Omnidirectional base",
  "Arm and interchangeable grippers (Robotiq 2F-85 / 140)",
  "NVIDIA Jetson TX2 · head cameras · tablet",
  "Payload: heineken beer, beverage can, water bottle",
  "Controller: mission_control",
];

export const collabContent = [
  {
    id: "0",
    title: "Keys stay off the robot",
    text: "The settler holds Circle’s entity secret and the peaq controller key. servebot-1 only sends a job id and a room.",
  },
  {
    id: "1",
    title: "USDC on Arc",
    text: "Guest funds lock in escrow on order. Pickup pays the kitchen 2.00 USDC. Delivery releases the rest.",
  },
  {
    id: "2",
    title: "A public machine",
    text: "peaq names the exact robot. The receipt is the machine page plus the Arc and peaq transaction hashes.",
  },
];

export const collabApps = [
  { id: "0", title: "peaq" },
  { id: "1", title: "Circle" },
  { id: "2", title: "Arc" },
  { id: "3", title: "Webots" },
];

export const pricing = [
  {
    id: "0",
    title: "Lock 6.00",
    description: "Guest USDC enters escrow before the robot moves.",
    amount: "6.00",
    unit: "USDC",
    links: [
      {
        label: "Arc deposit",
        href: "https://testnet.arcscan.app/tx/0x4285f5e6c7f30b6617722ada5f5f0f10980561f6ac79e5010a264ec494e5ef40",
      },
    ],
    features: [
      "deposit(jobId, machine, 6.00 USDC)",
      "Bound to servebot-1 from the first call",
      "No motion until the lock succeeds",
    ],
  },
  {
    id: "1",
    title: "Kitchen 2.00",
    description: "Pickup of the heineken pays the counter from the robot wallet.",
    amount: "2.00",
    unit: "USDC",
    links: [
      {
        label: "Arc vending",
        href: "https://testnet.arcscan.app/tx/0x513784057a66b3179a7d8279a875b6964f664f8650ec88eb0f4185c018c528c8",
      },
      {
        label: "peaq pickup",
        href: "https://peaq.subscan.io/tx/0x61877b9401345c2151d70adc593c98a2b09cc713cca46de7900b943c94827f24",
      },
    ],
    features: [
      "200 cents recorded on peaq",
      "Same job, not a second order",
      "Can and water ride along unpaid",
    ],
  },
  {
    id: "2",
    title: "Release",
    description: "Delivery splits the locked 6.00: operator, maker, robot reserve.",
    amount: "4.80",
    unit: "USDC",
    links: [
      {
        label: "Arc release",
        href: "https://testnet.arcscan.app/tx/0x1f34793b8a0cc2a1b15d77a8068efe45ede13163bd162fee10ea4033277ba927",
      },
      {
        label: "peaq delivery",
        href: "https://peaq.subscan.io/tx/0x404ca080f07f35a8d3a1a7cd6316f38d29295ab267102173d4a6670faedc6cfc",
      },
    ],
    features: [
      "4.80 operator · 0.60 maker · 0.60 reserve",
      "600 cents recorded on peaq",
      "A failed payment blocks the next order",
    ],
  },
];

export const agentChecklist = [
  { need: "Hold USDC", how: "Circle wallet on the settler, escrow on Arc" },
  { need: "Budget in the contract", how: "Release only after proved delivery" },
  { need: "Pay the kitchen", how: "2.00 USDC on heineken pickup" },
  { need: "Write the decision", how: "peaq revenue events, Arc tx hashes" },
  { need: "Escalate", how: "Failure stops the next order" },
];

export const benefits = [
  {
    id: "0",
    title: "A flat lease pays the idle robot",
    text: "One delivery and a hundred deliveries earn the same monthly fee. Speed and care go unpaid.",
    backgroundUrl: "/assets/benefits/card-1.svg",
    iconUrl: benefitIcon1,
    imageUrl: tiagoKitchen,
    imageAlt: "TIAGo reaching into a kitchen drawer",
  },
  {
    id: "1",
    title: "Pay per delivery needs a receipt",
    text: "Both sides need a record they did not write themselves. peaq names the machine. Arc shows the USDC.",
    backgroundUrl: "/assets/benefits/card-2.svg",
    iconUrl: benefitIcon2,
    imageUrl: tiagoPortrait,
    imageAlt: "TIAGo head and expansion panel",
    light: true,
  },
  {
    id: "2",
    title: "Kenya already has the rooms",
    text: "7.9 million visitors in 2025, about $3.8 billion, and more than 1,000 accredited hotels. The tray path has not changed.",
    backgroundUrl: "/assets/benefits/card-3.svg",
    iconUrl: benefitIcon3,
    imageUrl: tiagoFleet,
    imageAlt: "Two PAL robots on a workshop floor",
  },
  {
    id: "3",
    title: "Small jobs can still settle",
    text: "USDC on Arc is the fee and the payment. A two-dollar kitchen transfer does not wait on a volatile gas token.",
    backgroundUrl: "/assets/benefits/card-4.svg",
    iconUrl: benefitIcon4,
    imageUrl: tiagoHospitality,
    imageAlt: "TIAGo handing a cup at a hospitality counter",
    light: true,
  },
  {
    id: "4",
    title: "Failure stops the next order",
    text: "If escrow cannot lock or release, the settler refuses another job. A person is called only when policy says so.",
    backgroundUrl: "/assets/benefits/card-5.svg",
    iconUrl: benefitIcon1,
    imageUrl: tiagoHead,
    imageAlt: "TIAGo stereo cameras",
  },
  {
    id: "5",
    title: "One robot, one public id",
    text: "servebot-1 is a Machine NFT on peaq mainnet. The job is tied to that id, not to an unnamed wallet.",
    backgroundUrl: "/assets/benefits/card-6.svg",
    iconUrl: benefitIcon2,
    imageUrl: tiagoPlatform,
    imageAlt: "TIAGo platform diagram: base, arm, grippers, cameras",
  },
];

export const roadmap = [
  {
    id: "0",
    title: "Phase 0 — Hackathon",
    text: "One simulated run: hotel-ui order, Webots delivery, public Arc and peaq hashes. A guest who is not a developer can follow it.",
    date: "Now",
    status: "done",
    imageUrl: tiagoKitchen,
    caption: "Kitchen pickup — the moment the counter is paid",
    colorful: true,
  },
  {
    id: "1",
    title: "Phase 1 — Pilot",
    text: "Web3 Clubs Kenya lab, then a physical robot. Arc mainnet, a real USDC deposit, and three to five Nairobi hotel managers in the room.",
    date: "3–6 months",
    status: "progress",
    imageUrl: tiagoHospitality,
    caption: "The same job, outside the simulator",
  },
  {
    id: "2",
    title: "Phase 2 — Product",
    text: "Two or three Nairobi hotels. Pay per confirmed delivery: 2.00 standard, 4.00 premium, 1.50 on a fleet. One settler, many robots.",
    date: "6–18 months",
    status: "progress",
    imageUrl: tiagoFleet,
    caption: "A fleet shares one settlement agent",
  },
  {
    id: "3",
    title: "Phase 3 — Scale",
    text: "Kenya first, then any place a machine repeats a task and the receipt has value: warehouses, airports, wards, last mile.",
    date: "18 months+",
    status: "progress",
    imageUrl: tiagoPortrait,
    caption: "The machine keeps the same public identity",
  },
];

export const builderFacts = [
  {
    title: "NIRU National AI Hackathon",
    text: "Led a two-person team on Maritime Anomaly System, a drone and computer-vision project. Podium finish.",
  },
  {
    title: "Mashariki Cooperation Conference",
    text: "April 2026, Diani. Presented that system to an audience that included H.E. Dr. William Samoei Ruto, Hon. Onesimus Kipchumba Murkomen, and Mr. Noordin Mohamed Haji.",
  },
  {
    title: "ETH Safari",
    text: "Shipped at ETH Safari hackathons and won prizes, including the MetaMask prize.",
  },
];
