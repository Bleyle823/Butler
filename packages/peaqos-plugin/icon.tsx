import Image from "next/image";

export function PeaqosIcon({
  className,
}: {
  className?: string;
}): React.ReactElement {
  return (
    <Image
      alt="peaq"
      className={className}
      height={48}
      src="/protocols/peaq.png"
      width={48}
    />
  );
}
