import Image from "next/image";

export function CircleWalletsIcon({
  className,
}: {
  className?: string;
}): React.ReactElement {
  return (
    <Image
      alt="Circle"
      className={className}
      height={48}
      src="/protocols/circle.png"
      width={48}
    />
  );
}
