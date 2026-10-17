import Section from "./Section";
import Heading from "./Heading";
import { builderFacts } from "../constants";

const Builder = () => {
  return (
    <Section id="builder">
      <div className="container">
        <Heading
          tag="The builder"
          title="Bleyle Osewe"
        />
        <p className="body-1 max-w-3xl mx-auto -mt-10 mb-10 text-center text-n-2">
          Bachelor of Business Information Technology, class of 2024, Africa
          Nazarene University. Member of Web3 Clubs Kenya.
        </p>

        <div className="grid gap-6 md:grid-cols-3">
          {builderFacts.map((fact) => (
            <div
              key={fact.title}
              className="rounded-3xl border border-edge/40 bg-n-7 p-8"
            >
              <h4 className="h5 mb-4">{fact.title}</h4>
              <p className="body-2 text-n-3">{fact.text}</p>
            </div>
          ))}
        </div>

        <blockquote className="max-w-3xl mx-auto mt-12 body-2 text-n-2">
          “Butler is a Web3 Clubs project. The club intends to offer support
          beyond the hackathon. The club’s lab — including its dedicated
          robotics space — is available to Butler for pilot operations.”
          <footer className="mt-4 text-n-4">
            Web3 Clubs Kenya, October 2026
          </footer>
        </blockquote>

        <ul className="flex flex-wrap justify-center gap-x-8 gap-y-3 mt-10 font-code text-xs uppercase tracking-wider">
          <li>
            <a className="underline" href="mailto:Bennybleylle09@gmail.com">
              Bennybleylle09@gmail.com
            </a>
          </li>
          <li>
            <a className="underline" href="tel:+254705297628">
              0705297628
            </a>
          </li>
          <li>
            <a
              className="underline"
              href="https://web3clubs.xyz"
              target="_blank"
              rel="noreferrer"
            >
              web3clubs.xyz
            </a>
          </li>
          <li>
            <a
              className="underline"
              href="https://github.com/Bleyle823/Butler"
              target="_blank"
              rel="noreferrer"
            >
              github.com/Bleyle823/Butler
            </a>
          </li>
        </ul>
      </div>
    </Section>
  );
};

export default Builder;
