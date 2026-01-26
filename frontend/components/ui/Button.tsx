"use client";

import { ButtonHTMLAttributes, ReactNode } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "outline";
  size?: "sm" | "md" | "lg";
  children: ReactNode;
  isLoading?: boolean;
  leftIcon?: ReactNode;
}

export function Button({
  variant = "primary",
  size = "md",
  children,
  isLoading = false,
  leftIcon,
  className = "",
  disabled,
  ...props
}: ButtonProps) {
  const baseStyles =
    "inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-neutral-900 disabled:opacity-50 disabled:cursor-not-allowed";

  const variants = {
    primary:
      "bg-emerald-500 hover:bg-emerald-400 text-white focus:ring-emerald-500 active:scale-[0.98]",
    secondary:
      "bg-neutral-800 hover:bg-neutral-700 text-white focus:ring-neutral-500 active:scale-[0.98]",
    ghost:
      "bg-transparent hover:bg-neutral-800 text-neutral-300 hover:text-white focus:ring-neutral-500",
    outline:
      "bg-transparent border border-neutral-700 hover:border-neutral-500 text-neutral-300 hover:text-white focus:ring-neutral-500 active:scale-[0.98]",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm gap-1.5",
    md: "px-5 py-2.5 text-base gap-2",
    lg: "px-6 py-3 text-lg gap-2.5",
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <svg
          className="animate-spin h-5 w-5"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      ) : (
        leftIcon
      )}
      {children}
    </button>
  );
}
