import React from "react";

export interface FormProps extends React.FormHTMLAttributes<HTMLFormElement> {
  children: React.ReactNode;
  error?: string;
  className?: string;
}

const Form: React.FC<FormProps> = ({ children, error, className = "", ...props }) => (
  <form {...props} className={"space-y-4 " + className}>
    {error && (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-4">
        {error}
      </div>
    )}
    {children}
  </form>
);

export default Form;
