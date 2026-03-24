import { motion } from "framer-motion";
import { Brain, Zap, Shield, BarChart3, Clock, Users } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI-Powered Analysis",
    description: "Advanced NLP algorithms analyze resumes to extract skills, experience, and qualifications with high accuracy.",
  },
  {
    icon: Zap,
    title: "Instant Matching",
    description: "Get match scores in seconds using TF-IDF vectorization and cosine similarity for precise job matching.",
  },
  {
    icon: BarChart3,
    title: "Smart Ranking",
    description: "Candidates are automatically ranked based on their fit, saving hours of manual screening.",
  },
  {
    icon: Shield,
    title: "Bias-Free Screening",
    description: "Our AI focuses on skills and qualifications, helping reduce unconscious bias in the hiring process.",
  },
  {
    icon: Clock,
    title: "50% Time Saved",
    description: "Automate repetitive tasks and focus on what matters - connecting with the right candidates.",
  },
  {
    icon: Users,
    title: "Team Collaboration",
    description: "Share results with your team, add notes, and make hiring decisions together.",
  },
];

const Features = () => {
  return (
    <section className="py-24 bg-muted/30">
      <div className="container mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Why Choose Our Platform?
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Powerful features designed to streamline your recruitment process and find the best talent faster.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
              className="bg-card rounded-2xl p-8 border border-border shadow-card hover:shadow-lg transition-all duration-300"
            >
              <div className="w-14 h-14 rounded-xl bg-accent/10 flex items-center justify-center mb-6">
                <feature.icon className="w-7 h-7 text-accent" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-3">
                {feature.title}
              </h3>
              <p className="text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
