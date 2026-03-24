import { motion } from "framer-motion";
import { resumeGradeBands } from "@/lib/resume-grading";

const ResumeGradeGuide = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className="mt-8 rounded-3xl border border-border/70 bg-card/80 p-6 shadow-card backdrop-blur-sm"
    >
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-muted-foreground">
            Color Grading System
          </p>
          <h3 className="mt-2 text-2xl font-bold text-foreground">
            Instant visual grading for every resume
          </h3>
        </div>
        <p className="max-w-xl text-sm text-muted-foreground">
          Each file gets an ATS-style color band so recruiters can scan quality, fit, and urgency in seconds.
        </p>
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-5">
        {resumeGradeBands.map((grade) => {
          const Icon = grade.icon;

          return (
            <div
              key={grade.label}
              className={`rounded-2xl p-4 ${grade.surfaceClassName} ${grade.ringClassName}`}
            >
              <div className="flex items-center justify-between">
                <span className={`inline-flex min-w-11 items-center justify-center rounded-full px-3 py-1 text-sm font-bold ${grade.badgeClassName}`}>
                  {grade.label}
                </span>
                <Icon className={`h-4 w-4 ${grade.textClassName}`} />
              </div>
              <p className={`mt-4 text-sm font-semibold ${grade.textClassName}`}>{grade.band}</p>
              <p className="mt-1 text-xs text-muted-foreground">
                {grade.minScore === 0 ? "0-54 score" : `${grade.minScore}-100 score`}
              </p>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
};

export default ResumeGradeGuide;
