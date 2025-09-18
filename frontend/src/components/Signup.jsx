import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Signup.css";

const backendUrl = process.env.REACT_APP_API_URL || "https://fuzzy-space-engine-77w9qxrqq73xq96-8000.app.github.dev";

function Signup() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fullname: "",
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [errors, setErrors] = useState({ passwordMatch: true, serverError: "" });
  const [successMessage, setSuccessMessage] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });

    // Password match validation
    if (name === "password" || name === "confirmPassword") {
      setErrors({ ...errors, passwordMatch: formData.password === formData.confirmPassword });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({ ...errors, serverError: "" });

    // Final validation
    if (formData.password !== formData.confirmPassword) {
      setErrors({ ...errors, passwordMatch: false });
      return;
    }

    try {
      const response = await fetch(`${backendUrl}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fullname: formData.fullname,
          username: formData.username,
          email: formData.email,
          password: formData.password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Signup failed. Try again.");
      }

      setSuccessMessage("Signup successful! Redirecting to login...");
      
      // Delay navigation to show success message
      setTimeout(() => navigate("/login"), 2000); 

    } catch (error) {
      setErrors({ ...errors, serverError: error.message });
    }
  };

  return (
    <div className="signup-container">
      <h2>Sign Up</h2>
      <form onSubmit={handleSubmit}>
        <input type="text" name="fullname" placeholder="Full Name" value={formData.fullname} onChange={handleChange} required />
        <input type="text" name="username" placeholder="Username" value={formData.username} onChange={handleChange} required />
        <input type="email" name="email" placeholder="Email" value={formData.email} onChange={handleChange} required />
        <input type="password" name="password" placeholder="Password" value={formData.password} onChange={handleChange} required />
        <input type="password" name="confirmPassword" placeholder="Confirm Password" value={formData.confirmPassword} onChange={handleChange} required />
        
        {!errors.passwordMatch && <p className="error-text">Passwords do not match!</p>}
        {errors.serverError && <p className="error-text">{errors.serverError}</p>}
        {successMessage && <p className="success-text">{successMessage}</p>}

        <button type="submit">Sign Up</button>
      </form>
      <p>Already have an account? <span onClick={() => navigate("/login")}>Login</span></p>
    </div>
  );
}

export default Signup;
