import React from "react";

export interface AlertProps {
  message: string;
  type?: "error" | "success" | "info";
  className?: string;
}

const typeStyles = {
  error: "bg-red-50 border border-red-200 text-red-700",
  success: "bg-green-50 border border-green-200 text-green-700",
  info: "bg-blue-50 border border-blue-200 text-blue-700",
};

const Alert: React.FC<AlertProps> = ({ message, type = "error", className = "" }) => (
  <div className={`${typeStyles[type]} px-4 py-3 rounded-md mb-4 ${className}`}>
    {message}
  </div>
);

export default Alert;
