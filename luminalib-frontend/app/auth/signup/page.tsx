"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import Input from "@/components/Input";
import PasswordInput from "@/components/PasswordInput";
import Form from "@/components/Form";
import Alert from "@/components/Alert";

export default function SignupPage() {
  const { signup, isLoading, error } = useAuth();
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    full_name: "",
    password: "",
    confirmPassword: "",
  });
  const [formError, setFormError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setFormError(null);

    // Validation
    if (!formData.username || !formData.email || !formData.password) {
      setFormError("Please fill in all required fields");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setFormError("Passwords do not match");
      return;
    }

    if (formData.password.length < 8) {
      setFormError("Password must be at least 8 characters long");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setFormError("Please enter a valid email address");
      return;
    }

    const result = await signup({
      username: formData.username,
      email: formData.email,
      full_name: formData.full_name || undefined,
      password: formData.password,
    });

    if (!result.success) {
      setFormError(result.error || "Signup failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold text-center mb-2 text-slate-900">LuminalLib</h1>
        <p className="text-center text-slate-600 mb-8">Create your account</p>

        {(error || formError) && <Alert message={error || formError || ""} type="error" />}

        <Form onSubmit={handleSubmit}>
          <Input
            id="username"
            label="Username *"
            type="text"
            value={formData.username}
            onChange={e => setFormData({ ...formData, username: e.target.value })}
            placeholder="Choose a username"
            autoComplete="username"
          />
          <Input
            id="email"
            label="Email *"
            type="email"
            value={formData.email}
            onChange={e => setFormData({ ...formData, email: e.target.value })}
            placeholder="your@email.com"
            autoComplete="email"
          />
          <Input
            id="full_name"
            label="Full Name"
            type="text"
            value={formData.full_name}
            onChange={e => setFormData({ ...formData, full_name: e.target.value })}
            placeholder="Your full name"
            autoComplete="name"
          />
          <PasswordInput
            id="password"
            label="Password * (min 8 characters)"
            value={formData.password}
            onChange={e => setFormData({ ...formData, password: e.target.value })}
            placeholder="Enter a strong password"
            autoComplete="new-password"
          />
          <PasswordInput
            id="confirmPassword"
            label="Confirm Password *"
            value={formData.confirmPassword}
            onChange={e => setFormData({ ...formData, confirmPassword: e.target.value })}
            placeholder="Confirm your password"
            autoComplete="new-password"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white font-semibold py-2 rounded-md transition-colors"
          >
            {isLoading ? "Creating account..." : "Sign Up"}
          </button>
        </Form>

        <div className="mt-6 pt-6 border-t border-slate-200">
          <p className="text-center text-slate-600">
            Already have an account?{" "}
            <Link href="/auth/login" className="text-blue-600 hover:text-blue-700 font-semibold">
              Login
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
