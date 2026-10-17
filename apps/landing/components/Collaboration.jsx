import { butlerSymbol, check } from "../assets";
import { collabApps, collabContent, machineUrl } from "../constants";
import Button from "./Button";
import Section from "./Section";
import { LeftCurve, RightCurve } from "./design/Collaboration";

const Collaboration = () => {
  return (
    <Section crosses id="stack">
      <div className="container lg:flex">
        <div className="max-w-[25rem]">
          <h2 className="h2 mb-4 md:mb-8">
            The settler moves the money. The robot moves the tray.
          </h2>

          <ul className="max-w-[22rem] mb-10 md:mb-14">
            {collabContent.map((item) => (
              <li className="mb-3 py-3" key={item.id}>
                <div className="flex items-center">
                  <img src={check} width={24} height={24} alt="" />
                  <h6 className="body-2 ml-5">{item.title}</h6>
                </div>
                {item.text && (
                  <p className="body-2 mt-3 text-n-4">{item.text}</p>
                )}
              </li>
            ))}
          </ul>

          <Button href={machineUrl}>servebot-1 on peaq</Button>
        </div>

        <div className="lg:ml-auto xl:w-[38rem] mt-4">
          <p className="body-2 mb-8 text-n-4 md:mb-16 lg:mb-32 lg:w-[22rem] lg:mx-auto">
            hotel-ui posts the order. Webots proves pickup and delivery. Circle
            signs on Arc. peaq keeps the work record.
          </p>

          <div className="relative left-1/2 flex w-[22rem] aspect-square border border-n-6 rounded-full -translate-x-1/2 scale:75 md:scale-100">
            <div className="flex w-60 aspect-square m-auto border border-n-6 rounded-full">
              <div className="w-[6rem] aspect-square m-auto p-[0.2rem] bg-edge rounded-full">
                <div className="flex items-center justify-center w-full h-full bg-n-8 rounded-full">
                  <img
                    src={butlerSymbol}
                    width={48}
                    height={48}
                    alt="Butler"
                  />
                </div>
              </div>
            </div>

            <ul>
              {collabApps.map((app, index) => (
                <li
                  key={app.id}
                  className="absolute top-0 left-1/2 h-1/2 -ml-[1.6rem] origin-bottom"
                  style={{ transform: `rotate(${index * 90}deg)` }}
                >
                  <div
                    className="relative -top-[1.6rem] flex w-[3.2rem] h-[3.2rem] items-center justify-center bg-white border border-n-1/15 rounded-xl p-1.5"
                    style={{ transform: `rotate(-${index * 90}deg)` }}
                  >
                    <img
                      src={app.logo}
                      alt={app.title}
                      className="h-full w-full object-contain"
                      width={32}
                      height={32}
                    />
                  </div>
                </li>
              ))}
            </ul>

            <LeftCurve />
            <RightCurve />
          </div>
        </div>
      </div>
    </Section>
  );
};

export default Collaboration;
