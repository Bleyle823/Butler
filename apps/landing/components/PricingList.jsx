import { check } from "../assets";
import { pricing } from "../constants";

const PricingList = () => {
  return (
    <div className="flex gap-[1rem] max-lg:flex-wrap">
      {pricing.map((item) => (
        <div
          key={item.id}
          className="w-[19rem] max-lg:w-full h-full px-6 bg-n-7 border border-edge/35 rounded-3xl lg:w-auto even:py-14 odd:py-8 odd:my-4 [&>h4]:text-edge"
        >
          <h4 className="h4 mb-4">{item.title}</h4>

          <p className="body-2 min-h-[4rem] mb-3 text-n-1/50">
            {item.description}
          </p>

          <div className="flex items-end h-[5.5rem] mb-6">
            <div className="text-[4rem] leading-none font-bold">{item.amount}</div>
            <div className="h5 ml-2 mb-2">{item.unit}</div>
          </div>

          <div className="flex flex-col gap-3 mb-6">
            {item.links.map((link) => (
              <a
                key={link.href}
                href={link.href}
                target="_blank"
                rel="noreferrer"
                className="font-code text-xs font-bold uppercase tracking-wider text-n-1 underline"
              >
                {link.label}
              </a>
            ))}
          </div>

          <ul>
            {item.features.map((feature) => (
              <li
                key={feature}
                className="flex items-start py-5 border-t border-n-6"
              >
                <img src={check} width={24} height={24} alt="" />
                <p className="body-2 ml-4">{feature}</p>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default PricingList;
