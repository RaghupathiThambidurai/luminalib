import React from "react";
import Link from "next/link";

export interface HeaderProps {
  title?: string;
  children?: React.ReactNode;
  backLink?: { href: string; label: string };
  right?: React.ReactNode;
  className?: string;
}

const Header: React.FC<HeaderProps> = ({ title, children, backLink, right, className = "" }) => (
  <header className={"bg-white border-b border-slate-200 " + className}>
    <div className="max-w-6xl mx-auto px-4 py-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        {backLink && (
          <Link href={backLink.href} className="text-blue-600 hover:text-blue-700">
            {backLink.label}
          </Link>
        )}
        {title && <h1 className="text-3xl font-bold text-slate-900">{title}</h1>}
        {children}
      </div>
      {right && <div>{right}</div>}
    </div>
  </header>
);

export default Header;
