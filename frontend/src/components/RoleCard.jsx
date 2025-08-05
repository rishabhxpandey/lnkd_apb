import { motion } from 'framer-motion'
import { Check } from 'lucide-react'
import clsx from 'clsx'

const RoleCard = ({ role, isSelected, onSelect }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onSelect(role.id)}
      className={clsx(
        'card cursor-pointer relative transition-all duration-200',
        isSelected ? 'ring-2 ring-linkedin-blue shadow-xl' : 'hover:shadow-xl'
      )}
    >
      {isSelected && (
        <div className="absolute top-4 right-4">
          <div className="bg-linkedin-blue text-white rounded-full p-1">
            <Check size={20} />
          </div>
        </div>
      )}
      
      <div className="text-center mb-4">
        <span className="text-5xl">{role.icon}</span>
      </div>
      
      <h3 className="text-xl font-semibold mb-2 text-gray-900">
        {role.title}
      </h3>
      
      <p className="text-gray-600 mb-4">
        {role.description}
      </p>
      
      <div className="flex flex-wrap gap-2">
        {role.skills.map((skill, index) => (
          <span
            key={index}
            className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
          >
            {skill}
          </span>
        ))}
      </div>
    </motion.div>
  )
}

export default RoleCard 