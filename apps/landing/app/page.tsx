"use client";

import ButtonGradient from "../assets/svg/ButtonGradient";
import Benefits from "../components/Benefits";
import Builder from "../components/Builder";
import Collaboration from "../components/Collaboration";
import Footer from "../components/Footer";
import Header from "../components/Header";
import Hero from "../components/Hero";
import Pricing from "../components/Pricing";
import Roadmap from "../components/Roadmap";
import Services from "../components/Services";

export default function Page() {
  return (
    <>
      <div className="min-h-screen bg-n-8 pt-[4.75rem] lg:pt-[5.25rem] overflow-hidden">
        <Header />
        <Hero />
        <Benefits />
        <Collaboration />
        <Services />
        <Pricing />
        <Roadmap />
        <Builder />
        <Footer />
      </div>

      <ButtonGradient />
    </>
  );
}
