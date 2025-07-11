import React from "react";
import { Link } from "react-router-dom";
import "./LandingPage.css";
// Make sure you have the image at this path
import diaryImage from "../assets/diary-cover.jpg";

const LandingPage: React.FC = () => {
  return (
    <div className="landing-page">
      {/* ===== Hero Section ===== */}
      <section className="landing-container">
        <div className="landing-content">
          <div className="landing-image-container">
            <img
              src={diaryImage}
              alt="Anne Frank's Diary"
              className="landing-image"
            />
          </div>
          <div className="landing-text-container">
            <h1 className="landing-headline">A Journey Into History</h1>
            <p className="landing-subheading">
              "Paper has more patience than people."
            </p>
            <p className="landing-description">
              This educational experience offers a unique way to connect with
              the past. Through an AI-powered chat, explore the thoughts, hopes,
              and daily life of Anne Frank, based on the profound words from her
              diary.
            </p>
            <Link to="/chat" className="cta-button">
              Begin Conversation
            </Link>
          </div>
        </div>
      </section>

      {/* ===== Features Section ===== */}
      <section id="features" className="features-section">
        <h2 className="section-title">Why Talk with Anne?</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>Interactive Learning</h3>
            <p>
              Engage in a unique, conversational format to explore history from
              a deeply personal perspective, making learning memorable and
              impactful.
            </p>
          </div>
          <div className="feature-card">
            <h3>Historically Inspired</h3>
            <p>
              Every response is carefully crafted to reflect the tone,
              personality, and known experiences documented in Anne Frank's
              diary.
            </p>
          </div>
          <div className="feature-card">
            <h3>Respectful & Safe</h3>
            <p>
              A thoughtfully designed experience that prioritizes historical
              accuracy and respect to honor her memory and educate users
              responsibly.
            </p>
          </div>
        </div>
      </section>

      {/* ===== About Section ===== */}
      <section id="about" className="about-section">
        <h2 className="section-title">Our Mission</h2>
        <div className="about-content">
          <p>
            The "Talk with Anne" project was created to bridge the gap between
            historical texts and modern audiences. Our goal is to foster empathy
            and a deeper understanding of the human stories behind historical
            events. By simulating a conversation, we hope to make Anne's voice
            feel more present and her experiences more tangible for a new
            generation.
          </p>
          <p className="disclaimer">
            <strong>Please Note:</strong> This is an AI simulation. While based
            on her diary, it is an interpretation and not a substitute for
            reading her actual work. We encourage all users to read "The Diary
            of a Young Girl" to fully appreciate her powerful story.
          </p>
        </div>
      </section>

      {/* ===== Footer ===== */}
      <footer className="landing-footer">
        <p>
          © {new Date().getFullYear()} Talk with Anne. An Educational Project.
        </p>
      </footer>
    </div>
  );
};

export default LandingPage;
