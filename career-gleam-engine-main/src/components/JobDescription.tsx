import { useState } from "react";
import { motion } from "framer-motion";
import { Briefcase, MapPin, Clock, DollarSign, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";

const JobDescription = () => {
  const [jobTitle, setJobTitle] = useState("");
  const [location, setLocation] = useState("");
  const [experience, setExperience] = useState("");
  const [salary, setSalary] = useState("");
  const [description, setDescription] = useState("");

  const sampleDescription = `We are looking for a Senior Software Engineer to join our team.

Requirements:
• 5+ years of experience in software development
• Proficiency in React, TypeScript, and Node.js
• Experience with cloud services (AWS/GCP/Azure)
• Strong problem-solving and communication skills
• Bachelor's degree in Computer Science or related field

Nice to have:
• Experience with microservices architecture
• Knowledge of CI/CD pipelines
• Contributions to open source projects`;

  const fillSample = () => {
    setJobTitle("Senior Software Engineer");
    setLocation("San Francisco, CA (Remote)");
    setExperience("5+ years");
    setSalary("$150k - $200k");
    setDescription(sampleDescription);
  };

  return (
    <section className="py-24 bg-muted/30">
      <div className="container mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Define Your Requirements
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Enter the job description and requirements. Our AI will match candidates based on skills, experience, and qualifications.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="max-w-4xl mx-auto"
        >
          <div className="bg-card rounded-2xl border border-border shadow-card p-8">
            {/* Quick Fill Button */}
            <div className="flex justify-end mb-6">
              <Button variant="ghost" size="sm" onClick={fillSample} className="text-accent">
                <Sparkles className="w-4 h-4 mr-2" />
                Fill with sample
              </Button>
            </div>

            {/* Form Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground flex items-center gap-2">
                  <Briefcase className="w-4 h-4 text-accent" />
                  Job Title
                </label>
                <Input
                  placeholder="e.g., Senior Software Engineer"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="h-12"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-accent" />
                  Location
                </label>
                <Input
                  placeholder="e.g., San Francisco, CA"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="h-12"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground flex items-center gap-2">
                  <Clock className="w-4 h-4 text-accent" />
                  Experience Required
                </label>
                <Input
                  placeholder="e.g., 5+ years"
                  value={experience}
                  onChange={(e) => setExperience(e.target.value)}
                  className="h-12"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground flex items-center gap-2">
                  <DollarSign className="w-4 h-4 text-accent" />
                  Salary Range
                </label>
                <Input
                  placeholder="e.g., $150k - $200k"
                  value={salary}
                  onChange={(e) => setSalary(e.target.value)}
                  className="h-12"
                />
              </div>
            </div>

            {/* Description Textarea */}
            <div className="space-y-2 mb-8">
              <label className="text-sm font-medium text-foreground">
                Job Description & Requirements
              </label>
              <Textarea
                placeholder="Enter the full job description, responsibilities, and requirements..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="min-h-[200px] resize-none"
              />
            </div>

            {/* Action */}
            <div className="flex justify-center">
              <Button variant="gradient" size="lg" disabled={!description.trim()}>
                <Sparkles className="w-5 h-5" />
                Analyze & Match Candidates
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default JobDescription;
