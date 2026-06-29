import { motion } from 'framer-motion';

const defaultVariants = {
  hidden: { opacity: 0, y: 32 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] },
  },
};

export default function SectionReveal({
  children,
  className = '',
  delay = 0,
  as: Component = motion.section,
  id,
  ...props
}) {
  return (
    <Component
      id={id}
      className={className}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-8% 0px' }}
      variants={{
        hidden: defaultVariants.hidden,
        visible: {
          ...defaultVariants.visible,
          transition: { ...defaultVariants.visible.transition, delay },
        },
      }}
      {...props}
    >
      {children}
    </Component>
  );
}
