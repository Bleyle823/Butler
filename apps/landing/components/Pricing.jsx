import Section from "./Section";
import { tiagoPortrait, stars } from "../assets";
import Heading from "./Heading";
import PricingList from "./PricingList";
import { LeftLine, RightLine } from "./design/Pricing";
import { agentChecklist, jobId, machineUrl } from "../constants";

const Pricing = () => {
  return (
    <Section className="overflow-hidden" id="proof">
      <div className="container relative z-2">
        <div className="hidden relative justify-center mb-[6.5rem] lg:flex">
          <a href={machineUrl} target="_blank" rel="noreferrer">
            <img
              src={tiagoPortrait}
              className="relative z-1 w-[16rem] h-[16rem] rounded-full object-cover border border-edge/40"
              width={255}
              height={255}
              alt="servebot-1, the public face of the machine"
            />
          </a>
          <div className="absolute top-1/2 left-1/2 w-[60rem] -translate-x-1/2 -translate-y-1/2 pointer-events-none">
            <img
              src={stars}
              className="w-full"
              width={950}
              height={400}
              alt=""
            />
          </div>
        </div>

        <Heading
          tag="Recorded job"
          title="One order, three settlements"
        />
        <p className="body-2 max-w-3xl mx-auto -mt-8 mb-12 text-center text-n-3">
          Job {jobId}. Open the machine page, then each hash.
        </p>

        <div className="relative">
          <PricingList />
          <LeftLine />
          <RightLine />
        </div>

        <div className="mt-16 overflow-x-auto">
          <table className="w-full text-left body-2">
            <thead>
              <tr className="border-b border-n-6 text-n-1">
                <th className="py-3 pr-6 font-semibold">What the agent must do</th>
                <th className="py-3 font-semibold">What Butler does</th>
              </tr>
            </thead>
            <tbody>
              {agentChecklist.map((row) => (
                <tr key={row.need} className="border-b border-n-6/60 text-n-3">
                  <td className="py-4 pr-6 text-n-1">{row.need}</td>
                  <td className="py-4">{row.how}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Section>
  );
};

export default Pricing;
