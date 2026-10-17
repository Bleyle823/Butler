"use client";

import { curve, kitchenTrim } from "../assets";
import Button from "./Button";
import Section from "./Section";
import { BackgroundCircles, BottomLine, Gradient } from "./design/Hero";
import { heroIcons, hotelUiUrl } from "../constants";
import { ScrollParallax } from "react-just-parallax";
import { useRef } from "react";
import Generating from "./Generating";
import Notification from "./Notification";
import CompanyLogos from "./CompanyLogos";

const Hero = () => {
  const parallaxRef = useRef(null);

  return (
    <Section
      className="pt-[12rem] -mt-[5.25rem] overflow-hidden"
      crosses
      crossesOffset="lg:translate-y-[5.25rem]"
      customPaddings
      id="hero"
    >
      <div className="container relative" ref={parallaxRef}>
        <div className="relative z-1 max-w-[62rem] mx-auto text-center mb-[3.875rem] md:mb-20 lg:mb-[6.25rem]">
          <h1 className="h1 mb-6">
            The robot that gets paid when the {` `}
            <span className="inline-block relative">
              work is done.{" "}
              <img
                src={curve}
                className="absolute top-full left-0 w-full xl:-mt-2"
                width={624}
                height={28}
                alt="Curve"
              />
            </span>
          </h1>
          <p className="body-1 max-w-3xl mx-auto mb-6 text-n-2 lg:mb-8">
            Butler is a hotel service humanoid with payment built in. A guest
            orders a coffee; Circle holds the USDC, Arc escrow locks it on order,
            and releases when delivery is confirmed onchain. peaq names the exact
            machine on a public record—settlement runs on its own, and anyone can
            check the receipt. The robot delivered, and the robot got paid.
          </p>
          <Button href={hotelUiUrl} white>
            Place order
          </Button>
        </div>
        <div className="relative max-w-[23rem] mx-auto md:max-w-5xl xl:mb-24">
          <div className="relative z-1 p-0.5 rounded-3xl bg-edge overflow-hidden">
            <div className="relative bg-n-8 rounded-[1.375rem] overflow-hidden">
              <div className="h-[1.4rem] bg-n-10 rounded-t-[1.25rem]" />

              <div className="relative aspect-[33/40] rounded-b-[1.25rem] overflow-hidden md:aspect-[688/490] lg:aspect-[1024/490]">
                <video
                  src={kitchenTrim}
                  className="absolute inset-0 h-full w-full object-cover object-center"
                  autoPlay
                  muted
                  loop
                  playsInline
                  preload="metadata"
                  aria-label="servebot-1 kitchen delivery simulation"
                />

                <Generating className="absolute left-4 right-4 bottom-5 md:left-1/2 md:right-auto md:bottom-8 md:w-[31rem] md:-translate-x-1/2" />

                <ScrollParallax isAbsolutelyPositioned>
                  <ul className="hidden absolute -left-[5.5rem] bottom-[7.5rem] px-1 py-1 bg-n-7/90 backdrop-blur border border-edge/30 rounded-2xl xl:flex">
                    {heroIcons.map((icon, index) => (
                      <li className="p-5" key={index}>
                        <img src={icon} width={24} height={25} alt={icon} />
                      </li>
                    ))}
                  </ul>
                </ScrollParallax>

                <ScrollParallax isAbsolutelyPositioned>
                  <Notification
                    className="hidden absolute -right-[5.5rem] bottom-[11rem] w-[18rem] xl:flex"
                    title="6.00 USDC locked"
                  />
                </ScrollParallax>
              </div>
            </div>

            <Gradient />
          </div>
          <div
            className="absolute -top-[54%] left-1/2 w-[234%] -translate-x-1/2 md:-top-[46%] md:w-[138%] lg:-top-[104%] pointer-events-none"
            aria-hidden
          >
            <div
              className="w-full aspect-[4/5] bg-[radial-gradient(ellipse_80%_55%_at_50%_38%,rgba(107,143,132,0.14),transparent_58%),radial-gradient(ellipse_70%_45%_at_50%_72%,rgba(107,143,132,0.08),transparent_55%)]"
            />
          </div>

          <BackgroundCircles />
        </div>

        <CompanyLogos className="hidden relative z-10 mt-20 lg:block" />
      </div>

      <BottomLine />
    </Section>
  );
};

export default Hero;
