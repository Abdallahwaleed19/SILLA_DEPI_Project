// Original little-chef mouse. Replace with your own image: <img src="/mascot.png" />
export default function Mascot({ size = 280 }) {
  return (
    <svg viewBox="0 0 200 200" width={size} height={size} role="img" aria-label="Little chef mouse">
      <circle cx="100" cy="100" r="96" fill="#fff" />
      <circle cx="55" cy="84" r="26" fill="#9a8478" /><circle cx="145" cy="84" r="26" fill="#9a8478" />
      <circle cx="55" cy="84" r="15" fill="#f2b8b0" /><circle cx="145" cy="84" r="15" fill="#f2b8b0" />
      <ellipse cx="100" cy="122" rx="52" ry="46" fill="#b09a8c" />
      <ellipse cx="100" cy="136" rx="30" ry="24" fill="#efe2d3" />
      <circle cx="80" cy="112" r="6" fill="#30342F" /><circle cx="120" cy="112" r="6" fill="#30342F" />
      <circle cx="82" cy="110" r="2" fill="#fff" /><circle cx="122" cy="110" r="2" fill="#fff" />
      <ellipse cx="100" cy="128" rx="8" ry="6" fill="#d98c88" />
      <path d="M88 142q12 10 24 0" stroke="#30342F" strokeWidth="3" fill="none" strokeLinecap="round" />
      <g fill="#fff" stroke="#e3ddd0" strokeWidth="3">
        <circle cx="78" cy="52" r="17" /><circle cx="100" cy="42" r="19" /><circle cx="122" cy="52" r="17" />
        <rect x="68" y="62" width="64" height="16" rx="6" />
      </g>
    </svg>
  );
}
