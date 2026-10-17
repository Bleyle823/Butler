import { partnerBrands } from "../constants";

const CompanyLogos = ({ className }) => {
  return (
    <div className={className}>
      <h5 className="tagline mb-6 text-center text-n-1/50">
        Settlement, identity, and the room it runs in
      </h5>
      <ul className="flex flex-wrap items-center justify-center gap-x-10 gap-y-6">
        {partnerBrands.map((brand) => (
          <li key={brand.name}>
            {brand.logo ? (
              <img
                src={brand.logo}
                alt={brand.name}
                className="h-8 w-auto max-w-[7rem] object-contain opacity-90"
                width={120}
                height={32}
              />
            ) : (
              <span
                className="font-code text-sm uppercase tracking-wider text-n-1/80"
              >
                {brand.name}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CompanyLogos;
