import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import StudioPageHeader from '../components/StudioPageHeader';
import PipelineBar from '../components/PipelineBar';
import { PRODUCTS, studioPath } from '../../config/ecosystem';
import { HUMAN_TEAM, AI_TEAM, PIPELINE_STEPS } from '../../data/studioData';

export default function StudioPage() {
  return (
    <div className="space-y-8">
      <StudioPageHeader
        section="Team"
        title="Human & AI Team"
        description={`Your production company in one view — roles that power ${PRODUCTS.ORIGINALS.name}. Never shown to subscribers.`}
      />
      <PipelineBar />

      <section className="rounded-xl border dark:border-untold-border light:border-gray-200 p-6 dark:bg-untold-card/50">
        <h2 className="font-display text-xl font-bold dark:text-white light:text-black mb-6 text-center">
          Content Pipeline
        </h2>
        <div className="studio-pipeline">
          {PIPELINE_STEPS.map((step, i) => (
            <motion.div
              key={step}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
              className="studio-pipeline-step"
            >
              <span className="studio-pipeline-num">{i + 1}</span>
              <span>{step}</span>
            </motion.div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="font-display text-xl font-bold dark:text-white light:text-black mb-2">Human Team</h2>
        <p className="text-sm dark:text-untold-muted light:text-gray-500 mb-6">Creative leadership and production roles.</p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {HUMAN_TEAM.map((member) => (
            <article key={member.role} className="studio-card">
              <span className="text-2xl mb-3 block">{member.icon}</span>
              <h3 className="text-sm font-bold text-untold-gold uppercase tracking-wide">{member.role}</h3>
              <p className="dark:text-white light:text-black font-semibold mt-1">{member.name}</p>
              <p className="text-sm dark:text-untold-muted light:text-gray-500 mt-2 leading-relaxed">{member.bio}</p>
            </article>
          ))}
        </div>
      </section>

      <section>
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-6">
          <div>
            <h2 className="font-display text-xl font-bold dark:text-white light:text-black mb-2">AI Agents</h2>
            <p className="text-sm dark:text-untold-muted light:text-gray-500">Research through publishing automation.</p>
          </div>
          <Link to={studioPath('ai')} className="studio-admin-link">
            Open AI Command Center →
          </Link>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {AI_TEAM.map((agent) => (
            <article key={agent.id} className="studio-card studio-card--ai">
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className={`studio-agent-dot studio-agent-dot--${agent.status}`} />
                <span className="text-[10px] uppercase tracking-wider dark:text-untold-muted light:text-gray-400">{agent.status}</span>
              </div>
              <h3 className="dark:text-white light:text-black font-semibold text-sm">{agent.role}</h3>
              <p className="text-xs text-untold-gold mt-1">{agent.tasks} in queue</p>
              <p className="text-xs dark:text-untold-muted light:text-gray-500 mt-2 leading-relaxed">{agent.description}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
