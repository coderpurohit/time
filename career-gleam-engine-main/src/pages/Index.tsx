import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import ResumeUpload from "@/components/ResumeUpload";
import JobDescription from "@/components/JobDescription";
import CandidateRanking from "@/components/CandidateRanking";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <Hero />
      <Features />
      <ResumeUpload />
      <JobDescription />
      <CandidateRanking />
      <Footer />
    </div>
  );
};

export default Index;
