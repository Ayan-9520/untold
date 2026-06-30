import { JOB_STATUS_STYLES } from '../constants';

export default function JobStatusBadge({ status }) {
  const key = status?.toLowerCase?.() || status;
  return (
    <span className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full border ${JOB_STATUS_STYLES[key] || JOB_STATUS_STYLES.queued}`}>
      {key}
    </span>
  );
}
