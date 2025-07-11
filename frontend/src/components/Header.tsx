import React from "react";
import { Link, useLocation } from "react-router-dom";
import "./Header.css";

const Header: React.FC = () => {
  const location = useLocation();
  const isOnLandingPage = location.pathname === "/";

  // Function to handle smooth scrolling
  const handleScroll = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
    const element = document.getElementById(id);
    if (element) {
      // Calculate position, accounting for the sticky header's height
      const headerOffset = 80; // Adjust this value if your header height changes
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition =
        elementPosition + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: "smooth",
      });
    }
  };

  return (
    <header className="app-header">
      <Link to="/" className="logo-link">
        <h1 className="logo-text">Talk with Anne</h1>
      </Link>

      {isOnLandingPage && (
        <nav className="main-nav">
          <a href="#features" onClick={(e) => handleScroll(e, "features")}>
            Features
          </a>
          <a href="#about" onClick={(e) => handleScroll(e, "about")}>
            About
          </a>
          <Link to="/chat" className="nav-cta-button">
            Start Chat
          </Link>
        </nav>
      )}
    </header>
  );
};

export default Header;
