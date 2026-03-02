"use client";


import { useState, FormEvent } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import Input from "@/components/Input";
import PasswordInput from "@/components/PasswordInput";
import Form from "@/components/Form";
import Alert from "@/components/Alert";

export default function LoginPage() {
  const { login, isLoading, error } = useAuth();
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const [formError, setFormError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setFormError(null);

    if (!formData.username || !formData.password) {
      setFormError("Please fill in all fields");
      return;
    }

    const result = await login({
      username: formData.username,
      password: formData.password,
    });

    if (!result.success) {
      setFormError(result.error || "Login failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold text-center mb-2 text-slate-900">LuminalLib</h1>
        <p className="text-center text-slate-600 mb-8">Digital Library & Recommendations</p>

        {(error || formError) && <Alert message={error || formError || ""} type="error" />}

        <Form onSubmit={handleSubmit}>
          <Input
            id="username"
            label="Username"
            type="text"
            value={formData.username}
            onChange={e => setFormData({ ...formData, username: e.target.value })}
            placeholder="Enter your username"
            autoComplete="username"
          />
          <PasswordInput
            id="password"
            label="Password"
            value={formData.password}
            onChange={e => setFormData({ ...formData, password: e.target.value })}
            placeholder="Enter your password"
            autoComplete="current-password"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-semibold py-2 rounded-md transition-colors"
          >
            {isLoading ? "Logging in..." : "Login"}
          </button>
        </Form>

        <div className="mt-6 pt-6 border-t border-slate-200">
          <p className="text-center text-slate-600">
            Don't have an account?{" "}
            <Link href="/auth/signup" className="text-blue-600 hover:text-blue-700 font-semibold">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
