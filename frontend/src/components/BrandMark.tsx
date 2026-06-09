import { useId } from "react";

interface BrandMarkProps {
  compact?: boolean;
  size?: "small" | "default" | "large";
  className?: string;
}

export function BrandMark({ compact = false, size = "default", className = "" }: BrandMarkProps) {
  const svgId = useId().replace(/:/g, "");
  const bgId = `${svgId}-seal-bg`;
  const goldId = `${svgId}-seal-gold`;

  return (
    <span className={`brand-mark brand-mark--${size} ${compact ? "brand-mark--compact" : ""} ${className}`.trim()}>
      <span className="brand-mark__seal" aria-hidden="true">
        <svg viewBox="0 0 80 80" role="img">
          <defs>
            <linearGradient id={bgId} x1="15" y1="8" x2="66" y2="72" gradientUnits="userSpaceOnUse">
              <stop stopColor="#2a5b52" />
              <stop offset="1" stopColor="#102e2a" />
            </linearGradient>
            <linearGradient id={goldId} x1="14" y1="10" x2="68" y2="72" gradientUnits="userSpaceOnUse">
              <stop stopColor="#f7dfaa" />
              <stop offset="0.5" stopColor="#c8a467" />
              <stop offset="1" stopColor="#8e6b35" />
            </linearGradient>
          </defs>
          <rect x="7" y="7" width="66" height="66" rx="14" fill={`url(#${bgId})`} />
          <rect x="9.5" y="9.5" width="61" height="61" rx="12" fill="none" stroke={`url(#${goldId})`} strokeWidth="3" />
          <path
            d="M20 20c7-3 13-2 20 3 7-5 13-6 20-3v14c-7-3-13-2-20 3-7-5-13-6-20-3V20Z"
            fill="#fff8e7"
            stroke={`url(#${goldId})`}
            strokeWidth="2"
            strokeLinejoin="round"
          />
          <path d="M40 23v43" stroke={`url(#${goldId})`} strokeWidth="2.5" strokeLinecap="round" />
          <path d="M35 39c0-4 2.5-6.5 5-6.5s5 2.5 5 6.5-2.5 6-5 6-5 2.5-5 6.5 2.5 6.5 5 6.5 5-2.5 5-6.5" fill="none" stroke="#fff1c7" strokeWidth="2.2" strokeLinecap="round" />
          <text x="21" y="60" fill="#f4d99e" fontSize="29" fontWeight="800" fontFamily="Songti SC, STSong, serif">毅</text>
          <text x="42" y="60" fill="#f4d99e" fontSize="29" fontWeight="800" fontFamily="Songti SC, STSong, serif">医</text>
        </svg>
      </span>
      {compact ? null : (
        <span className="brand-mark__text">
          <strong>毅医</strong>
          <i />
          <small>医学教育 · 智能题库平台</small>
        </span>
      )}
    </span>
  );
}