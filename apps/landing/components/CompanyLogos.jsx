import { partners } from "../constants";

const CompanyLogos = ({ className }) => {
  return (
    <div className={className}>
      <h5 className="tagline mb-6 text-center text-n-1/50">
        Settlement, identity, and the room it runs in
      </h5>
      <ul className="flex flex-wrap justify-center gap-x-10 gap-y-4">
        {partners.map((name) => (
          <li
            className="font-code text-sm uppercase tracking-wider text-n-1/80"
            key={name}
          >
            {name}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CompanyLogos;
