import Section from "./Section";
import Heading from "./Heading";
import { tiagoHead, tiagoHospitality, tiagoPlatform } from "../assets";
import { machineUrl, specLines } from "../constants";
import {
  PhotoChatMessage,
  Gradient,
  VideoBar,
  VideoChatMessage,
} from "./design/Services";

import Generating from "./Generating";

const Services = () => {
  return (
    <Section id="demo">
      <div className="container">
        <Heading
          title="servebot-1, in the kitchen."
          text="Webots R2025a. Rooms 1204, 1205, and 1206. The robot does not enter them."
        />

        <div className="relative">
          <div className="relative z-1 flex items-center h-[39rem] mb-5 border border-edge/40 rounded-3xl overflow-hidden bg-[#f0eeea] xl:h-[46rem]">
            <img
              className="absolute inset-0 w-full h-full object-contain object-center p-4 md:p-8 lg:p-10"
              width={1200}
              height={800}
              alt="PAL Robotics TIAGo — servebot-1 platform"
              src={tiagoPlatform}
            />

            <div className="absolute left-4 right-4 bottom-20 z-1 max-w-xl rounded-2xl bg-n-8/90 p-4 backdrop-blur lg:left-8 lg:bottom-24">
              <h4 className="h5 mb-2">servebot-1 · TIAGo</h4>
              <ul className="body-2 text-n-3">
                {specLines.map((line) => (
                  <li key={line}>{line}</li>
                ))}
              </ul>
              <a
                className="mt-3 inline-block font-code text-xs uppercase tracking-wider text-n-1 underline"
                href={machineUrl}
                target="_blank"
                rel="noreferrer"
              >
                Machine NFT on peaq
              </a>
            </div>

            <Generating className="absolute left-4 right-4 bottom-4 z-1 border-edge/30 border lg:left-1/2 lg:right-auto lg:bottom-8 lg:-translate-x-1/2" />
          </div>

          <div className="relative z-1 grid gap-5 lg:grid-cols-2">
            <div className="relative min-h-[39rem] border border-edge/40 rounded-3xl overflow-hidden">
              <div className="absolute inset-0">
                <img
                  src={tiagoHead}
                  className="h-full w-full object-cover"
                  width={630}
                  height={750}
                  alt="TIAGo stereo cameras — how pickup and delivery are seen"
                />
              </div>

              <div className="absolute inset-0 flex flex-col justify-end p-8 bg-gradient-to-b from-n-8/0 to-n-8/90 lg:p-15">
                <h4 className="h4 mb-4">Sees the counter and the table</h4>
                <p className="body-2 mb-[3rem] text-n-3">
                  The head cameras are how the simulation knows the heineken
                  left the counter and later rested on the table.
                </p>
              </div>

              <PhotoChatMessage />
            </div>

            <div className="p-4 bg-n-7 rounded-3xl overflow-hidden lg:min-h-[46rem]">
              <div className="py-12 px-4 xl:px-8">
                <h4 className="h4 mb-4">The job in the real world</h4>
                <p className="body-2 text-n-3">
                  A person, a cup, a robot at a service counter. The simulation
                  is the same task: collect, carry, set down, then get paid.
                </p>
              </div>

              <div className="relative h-[20rem] bg-n-8 rounded-xl overflow-hidden md:h-[25rem]">
                <img
                  src={tiagoHospitality}
                  className="w-full h-full object-cover"
                  width={520}
                  height={400}
                  alt="TIAGo handing a cup across a hospitality counter"
                />

                <VideoChatMessage />
                <VideoBar />
              </div>
            </div>
          </div>

          <Gradient />
        </div>
      </div>
    </Section>
  );
};

export default Services;
