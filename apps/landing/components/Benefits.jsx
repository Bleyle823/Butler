import { benefits } from "../constants";
import Heading from "./Heading";
import Section from "./Section";
import Arrow from "../assets/svg/Arrow";
import { GradientLight } from "./design/Benefits";

const cardOuter =
  "relative md:max-w-[24rem] rounded-3xl p-0.5 bg-edge overflow-hidden";
const cardInner =
  "relative flex flex-col min-h-[22rem] rounded-[1.375rem] bg-n-8 p-[2.4rem] overflow-hidden";

const Benefits = () => {
  return (
    <Section id="features">
      <div className="container relative z-2">
        <Heading
          className="md:max-w-md lg:max-w-2xl"
          title="Chat Smarter, Not Harder with Butler"
        />

        <div className="flex flex-wrap gap-10 mb-10">
          {benefits.map((item) => (
            <div className={cardOuter} key={item.id}>
              <div className={`${cardInner} pointer-events-none`}>
                <h5 className="h5 mb-5 relative z-2">{item.title}</h5>
                <p className="body-2 mb-6 text-n-3 relative z-2">{item.text}</p>
                <div className="flex items-center mt-auto relative z-2">
                  <img
                    src={item.iconUrl}
                    width={48}
                    height={48}
                    alt={item.title}
                  />
                  <p className="ml-auto font-code text-xs font-bold text-n-1 uppercase tracking-wider">
                    Explore more
                  </p>
                  <Arrow />
                </div>

                {item.light && <GradientLight />}

                {item.imageUrl && (
                  <div className="absolute inset-0 z-1 opacity-0 transition-opacity hover:opacity-10 pointer-events-none">
                    <img
                      src={item.imageUrl}
                      width={380}
                      height={362}
                      alt={item.title}
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </Section>
  );
};

export default Benefits;
