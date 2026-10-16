import type { ButtonHTMLAttributes, ReactNode } from "react";
import ButtonSvg from "../assets/svg/ButtonSvg";

type ButtonProps = {
  className?: string;
  href?: string;
  onClick?: () => void;
  children: ReactNode;
  px?: string;
  white?: boolean;
  disabled?: boolean;
  type?: ButtonHTMLAttributes<HTMLButtonElement>["type"];
};

const Button = ({
  className,
  href,
  onClick,
  children,
  px,
  white,
  disabled,
  type = "button",
}: ButtonProps) => {
  const classes = `button relative inline-flex items-center justify-center h-11 transition-colors hover:text-color-1 disabled:opacity-50 disabled:pointer-events-none ${
    px || "px-7"
  } ${white ? "text-n-8" : "text-n-1 hover:text-edge"} ${className || ""}`;
  const spanClasses = "relative z-10";

  if (href) {
    return (
      <a href={href} className={classes}>
        <span className={spanClasses}>{children}</span>
        {ButtonSvg(white)}
      </a>
    );
  }

  return (
    <button
      className={classes}
      onClick={onClick}
      disabled={disabled}
      type={type}
    >
      <span className={spanClasses}>{children}</span>
      {ButtonSvg(white)}
    </button>
  );
};

export default Button;
