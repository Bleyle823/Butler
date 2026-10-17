import Logo from "./Logo";
import { landingUrl } from "../constants";
import Button from "./Button";

const OrderHeader = () => {
  return (
    <div
      className="fixed top-0 left-0 w-full z-50 border-b border-n-6 bg-n-8/90 backdrop-blur-sm"
    >
      <div className="flex items-center px-5 lg:px-7.5 xl:px-10 max-lg:py-4 lg:h-[5.25rem]">
        <a className="block xl:mr-8" href={landingUrl}>
          <Logo />
        </a>

        <nav className="hidden lg:flex lg:mx-auto">
          <a
            href={landingUrl}
            className="block relative font-code text-xs font-semibold uppercase text-n-1/50 leading-5 transition-colors hover:text-n-1 xl:px-12"
          >
            Back to site
          </a>
        </nav>

        <Button className="ml-auto hidden lg:flex" href={landingUrl}>
          Back to site
        </Button>

        <Button className="ml-auto lg:hidden" px="px-5" href={landingUrl}>
          Back
        </Button>
      </div>
    </div>
  );
};

export default OrderHeader;
