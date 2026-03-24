import { motion } from "framer-motion";
import { Star, Award, TrendingUp, Mail, Linkedin, ExternalLink, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";
import { getResumeGradeSummary } from "@/lib/resume-grading";

interface Candidate {
  id: number;
  name: string;
  role: string;
  avatar: string;
  matchScore: number;
  experience: string;
  location: string;
  skills: string[];
  education: string;
  email: string;
}

const mockCandidates: Candidate[] = [
  {
    id: 1,
    name: "Sarah Chen",
    role: "Senior Software Engineer",
    avatar: "SC",
    matchScore: 95,
    experience: "7 years",
    location: "San Francisco, CA",
    skills: ["React", "TypeScript", "Node.js", "AWS", "Python"],
    education: "MS Computer Science, Stanford",
    email: "sarah.chen@email.com",
  },
  {
    id: 2,
    name: "Marcus Rodriguez",
    role: "Full Stack Developer",
    avatar: "MR",
    matchScore: 88,
    experience: "5 years",
    location: "Austin, TX",
    skills: ["React", "TypeScript", "PostgreSQL", "Docker", "GCP"],
    education: "BS Software Engineering, UT Austin",
    email: "marcus.r@email.com",
  },
  {
    id: 3,
    name: "Emily Watson",
    role: "Software Engineer II",
    avatar: "EW",
    matchScore: 82,
    experience: "4 years",
    location: "Seattle, WA",
    skills: ["React", "JavaScript", "Node.js", "MongoDB", "Redis"],
    education: "BS Computer Science, UW",
    email: "emily.w@email.com",
  },
  {
    id: 4,
    name: "David Kim",
    role: "Backend Engineer",
    avatar: "DK",
    matchScore: 76,
    experience: "6 years",
    location: "New York, NY",
    skills: ["Python", "Django", "PostgreSQL", "AWS", "Kubernetes"],
    education: "BS Computer Engineering, NYU",
    email: "david.kim@email.com",
  },
  {
    id: 5,
    name: "Jessica Liu",
    role: "Frontend Developer",
    avatar: "JL",
    matchScore: 71,
    experience: "3 years",
    location: "Los Angeles, CA",
    skills: ["React", "Vue.js", "CSS", "Figma", "JavaScript"],
    education: "BA Digital Media, UCLA",
    email: "jessica.liu@email.com",
  },
];

const getScoreBadge = (score: number) => {
  if (score >= 90) return { icon: Star, label: "Excellent Match" };
  if (score >= 80) return { icon: Award, label: "Strong Match" };
  if (score >= 70) return { icon: TrendingUp, label: "Good Match" };
  return { icon: TrendingUp, label: "Potential" };
};

const CandidateCard = ({ candidate, index }: { candidate: Candidate; index: number }) => {
  const [expanded, setExpanded] = useState(false);
  const scoreBadge = getScoreBadge(candidate.matchScore);
  const grade = getResumeGradeSummary(candidate.matchScore);
  const GradeIcon = grade.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      className={`bg-card rounded-2xl border border-border shadow-card overflow-hidden hover:shadow-lg transition-all duration-300 ${grade.ringClassName}`}
    >
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-4">
            {/* Avatar */}
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-accent/80 to-accent flex items-center justify-center text-accent-foreground font-bold text-lg">
              {candidate.avatar}
            </div>
            <div>
              <h3 className="font-semibold text-lg text-foreground">{candidate.name}</h3>
              <p className="text-muted-foreground">{candidate.role}</p>
            </div>
          </div>

          {/* Match Score */}
          <div className="text-center">
            <div className={`w-16 h-16 rounded-xl ${grade.badgeClassName} flex items-center justify-center text-2xl font-bold shadow-lg`}>
              {candidate.matchScore}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Match %</p>
          </div>
        </div>

        {/* Quick Info */}
        <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
          <span>{candidate.experience} experience</span>
          <span>•</span>
          <span>{candidate.location}</span>
        </div>

        {/* Skills */}
        <div className="flex flex-wrap gap-2 mb-4">
          {candidate.skills.slice(0, 4).map((skill) => (
            <Badge key={skill} variant="secondary" className="rounded-lg">
              {skill}
            </Badge>
          ))}
          {candidate.skills.length > 4 && (
            <Badge variant="outline" className="rounded-lg">
              +{candidate.skills.length - 4} more
            </Badge>
          )}
        </div>

        {/* Score Badge */}
        <div className="flex flex-wrap items-center gap-2 mb-4">
          <scoreBadge.icon className="w-4 h-4 text-accent" />
          <span className="text-sm font-medium text-accent">{scoreBadge.label}</span>
          <div className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ${grade.surfaceClassName} ${grade.textClassName}`}>
            <GradeIcon className="h-3.5 w-3.5" />
            <span>{grade.label} grade</span>
          </div>
        </div>

        <div className="mb-4">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Resume quality grade</span>
            <span className={`font-semibold ${grade.textClassName}`}>{grade.band}</span>
          </div>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-muted">
            <div
              className={`h-full rounded-full ${grade.progressClassName}`}
              style={{ width: `${candidate.matchScore}%` }}
            />
          </div>
        </div>

        {/* Expandable Details */}
        <motion.div
          initial={false}
          animate={{ height: expanded ? "auto" : 0 }}
          className="overflow-hidden"
        >
          <div className="pt-4 border-t border-border">
            <div className="grid grid-cols-2 gap-4 text-sm mb-4">
              <div>
                <span className="text-muted-foreground">Education:</span>
                <p className="font-medium text-foreground">{candidate.education}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Email:</span>
                <p className="font-medium text-foreground">{candidate.email}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button size="sm" variant="default">
                <Mail className="w-4 h-4" />
                Contact
              </Button>
              <Button size="sm" variant="outline">
                <Linkedin className="w-4 h-4" />
                LinkedIn
              </Button>
              <Button size="sm" variant="ghost">
                <ExternalLink className="w-4 h-4" />
                View Resume
              </Button>
            </div>
          </div>
        </motion.div>

        {/* Expand Button */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full pt-4 flex items-center justify-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <span>{expanded ? "Show less" : "Show more"}</span>
          <ChevronDown className={`w-4 h-4 transition-transform ${expanded ? "rotate-180" : ""}`} />
        </button>
      </div>
    </motion.div>
  );
};

const CandidateRanking = () => {
  return (
    <section className="py-24 bg-background">
      <div className="container mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/10 mb-4">
            <TrendingUp className="w-4 h-4 text-accent" />
            <span className="text-sm font-medium text-accent">AI-Ranked Results</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Top Candidates
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Our AI has analyzed and ranked candidates based on their match with your job requirements.
          </p>
        </motion.div>

        <div className="max-w-4xl mx-auto grid gap-6">
          {mockCandidates.map((candidate, index) => (
            <CandidateCard key={candidate.id} candidate={candidate} index={index} />
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mt-12"
        >
          <Button variant="outline" size="lg">
            Export Results to CSV
          </Button>
        </motion.div>
      </div>
    </section>
  );
};

export default CandidateRanking;
