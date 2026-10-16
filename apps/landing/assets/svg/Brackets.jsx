const ACCENT = "#6B8F84";

const brackets = (position) =>
  position === "left" ? (
    <svg
      width="5"
      height="14"
      viewBox="0 0 5 14"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path d="M5 0.822266H1V12.8223H5" stroke={ACCENT} />
    </svg>
  ) : (
    <svg
      width="5"
      height="14"
      viewBox="0 0 5 14"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M-2.98023e-08 0.822266H4V12.8223H-2.98023e-08"
        stroke={ACCENT}
      />
    </svg>
  );

export default brackets;
