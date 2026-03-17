import React from "react";

type Props = React.InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string;
};

export default function Input({ label, error, className, ...props }: Props) {
  return (
    <div>
      {label && (
        <label className="block text-sm font-medium text-slate-700 mb-1">
          {label}
        </label>
      )}
      <input
        {...props}
        className={
          "w-full px-4 py-2 border rounded-md text-black focus:outline-none focus:ring-2 " +
          (error
            ? "border-red-300 focus:ring-red-500"
            : "border-slate-300 focus:ring-blue-500") +
          " text-black " +
          (className ?? "")
        }
      />
      {error && <div className="text-xs text-red-600 mt-1">{error}</div>}
    </div>
  );
}