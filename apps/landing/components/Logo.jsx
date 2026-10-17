import { butlerSymbol } from "../assets";

const Logo = ({ className = "" }) => (
  <span className={`inline-flex items-center gap-2.5 ${className}`}>
    <img
      src={butlerSymbol}
      width={40}
      height={40}
      alt=""
      aria-hidden="true"
      className="shrink-0"
    />
    <span className="text-[1.625rem] font-semibold leading-none text-n-1 tracking-[-0.02em]">
      Butler
    </span>
  </span>
);

export default Logo;
