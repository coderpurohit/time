import { Award, BadgeCheck, ShieldAlert, Sparkles, TrendingUp, type LucideIcon } from "lucide-react";

export interface ResumeGrade {
  label: string;
  band: string;
  minScore: number;
  icon: LucideIcon;
  badgeClassName: string;
  surfaceClassName: string;
  ringClassName: string;
  textClassName: string;
  progressClassName: string;
}

const gradeBands: ResumeGrade[] = [
  {
    label: "A+",
    band: "Elite",
    minScore: 90,
    icon: Sparkles,
    badgeClassName: "bg-grade-elite text-white shadow-[0_12px_30px_-16px_hsl(var(--grade-elite)/0.9)]",
    surfaceClassName: "bg-[hsl(var(--grade-elite-soft))]",
    ringClassName: "ring-1 ring-[hsl(var(--grade-elite)/0.28)]",
    textClassName: "text-[hsl(var(--grade-elite-ink))]",
    progressClassName: "bg-grade-elite",
  },
  {
    label: "A",
    band: "Excellent",
    minScore: 80,
    icon: Award,
    badgeClassName: "bg-grade-strong text-white shadow-[0_12px_30px_-16px_hsl(var(--grade-strong)/0.85)]",
    surfaceClassName: "bg-[hsl(var(--grade-strong-soft))]",
    ringClassName: "ring-1 ring-[hsl(var(--grade-strong)/0.24)]",
    textClassName: "text-[hsl(var(--grade-strong-ink))]",
    progressClassName: "bg-grade-strong",
  },
  {
    label: "B",
    band: "Strong",
    minScore: 70,
    icon: TrendingUp,
    badgeClassName: "bg-grade-solid text-slate-950 shadow-[0_12px_30px_-16px_hsl(var(--grade-solid)/0.75)]",
    surfaceClassName: "bg-[hsl(var(--grade-solid-soft))]",
    ringClassName: "ring-1 ring-[hsl(var(--grade-solid)/0.28)]",
    textClassName: "text-[hsl(var(--grade-solid-ink))]",
    progressClassName: "bg-grade-solid",
  },
  {
    label: "C",
    band: "Needs Work",
    minScore: 55,
    icon: BadgeCheck,
    badgeClassName: "bg-grade-fair text-slate-950 shadow-[0_12px_30px_-16px_hsl(var(--grade-fair)/0.75)]",
    surfaceClassName: "bg-[hsl(var(--grade-fair-soft))]",
    ringClassName: "ring-1 ring-[hsl(var(--grade-fair)/0.28)]",
    textClassName: "text-[hsl(var(--grade-fair-ink))]",
    progressClassName: "bg-grade-fair",
  },
  {
    label: "D",
    band: "At Risk",
    minScore: 0,
    icon: ShieldAlert,
    badgeClassName: "bg-grade-risk text-white shadow-[0_12px_30px_-16px_hsl(var(--grade-risk)/0.85)]",
    surfaceClassName: "bg-[hsl(var(--grade-risk-soft))]",
    ringClassName: "ring-1 ring-[hsl(var(--grade-risk)/0.22)]",
    textClassName: "text-[hsl(var(--grade-risk-ink))]",
    progressClassName: "bg-grade-risk",
  },
];

export const getResumeGrade = (score: number): ResumeGrade =>
  gradeBands.find((grade) => score >= grade.minScore) ?? gradeBands[gradeBands.length - 1];

export const getResumeGradeSummary = (score: number) => {
  const grade = getResumeGrade(score);

  if (score >= 90) return { ...grade, description: "Outstanding ATS fit with strong keyword coverage and structure." };
  if (score >= 80) return { ...grade, description: "Very competitive resume with only small optimization gaps left." };
  if (score >= 70) return { ...grade, description: "Solid baseline resume that benefits from targeted polishing." };
  if (score >= 55) return { ...grade, description: "Readable foundation, but impact and alignment need more work." };

  return { ...grade, description: "Low-fit resume that should be revised before submission." };
};

export const resumeGradeBands = gradeBands;
