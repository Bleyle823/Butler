import Section from "./Section";
import { machineUrl } from "../constants";

const links = [
  { title: "servebot-1", href: machineUrl },
  { title: "Arc testnet", href: "https://testnet.arcscan.app" },
  { title: "peaq", href: "https://peaq.subscan.io" },
  { title: "Web3 Clubs", href: "https://web3clubs.xyz" },
];

const Footer = () => {
  return (
    <Section crosses className="!px-0 !py-10">
      <div className="container flex sm:justify-between justify-center items-center gap-10 max-sm:flex-col">
        <p className="caption text-n-4 lg:block">
          Butler · servebot-1 · Web3 Clubs Kenya · {new Date().getFullYear()}
        </p>

        <ul className="flex gap-5 flex-wrap">
          {links.map((item) => (
            <li key={item.href}>
              <a
                href={item.href}
                target="_blank"
                rel="noreferrer"
                className="font-code text-xs uppercase tracking-wider text-n-1/70 hover:text-n-1"
              >
                {item.title}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </Section>
  );
};

export default Footer;
