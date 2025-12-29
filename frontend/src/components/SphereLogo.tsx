import React from 'react';

const SphereLogo: React.FC<{ className?: string }> = ({ className = "w-16 h-16" }) => {
  return (
    <svg
      className={className}
      viewBox="0 0 200 200"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Outer circle - medical cross background */}
      <circle cx="100" cy="100" r="95" fill="url(#gradient1)" />
      
      {/* Medical cross */}
      <path
        d="M100 40 L100 160 M40 100 L160 100"
        stroke="white"
        strokeWidth="20"
        strokeLinecap="round"
      />
      
      {/* Inner circle - shield */}
      <circle cx="100" cy="100" r="60" fill="url(#gradient2)" opacity="0.9" />
      
      {/* Heartbeat line */}
      <path
        d="M60 100 L75 100 L82 85 L88 115 L94 95 L100 105 L106 100 L140 100"
        stroke="white"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      
      {/* Gradients */}
      <defs>
        <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#667eea" />
          <stop offset="100%" stopColor="#764ba2" />
        </linearGradient>
        <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#4F46E5" />
          <stop offset="100%" stopColor="#7C3AED" />
        </linearGradient>
      </defs>
    </svg>
  );
};

export default SphereLogo;