import React from "react";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  className?: string;
}

const Input: React.FC<InputProps> = ({ label, error, className = "", ...props }) => (
  <div className={"mb-4 " + className}>
    {label && (
      <label htmlFor={props.id} className="block text-sm font-medium text-slate-700 mb-1">
        {label}
      </label>
    )}
    <input
      {...props}
      className={
        "w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 " +
        (error
          ? "border-red-400 focus:ring-red-500"
          : "border-slate-300 focus:ring-blue-500") +
        " text-black " +
        (props.className || "")
      }
    />
    {error && <div className="text-xs text-red-600 mt-1">{error}</div>}
  </div>
);

export default Input;
