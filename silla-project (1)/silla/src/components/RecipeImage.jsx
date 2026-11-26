import { useState } from "react";

export default function RecipeImage({
  src,
  alt,
  emoji = "🍽️",
  recipeId,
  reason,
  className = "",
  fallbackClassName = "",
  loading = "lazy",
}) {
  const [failedSrc, setFailedSrc] = useState(null);
  const hue = [...String(recipeId || alt || "recipe")].reduce((value, char) => value + char.charCodeAt(0), 0) % 360;

  if (!src || failedSrc === src) {
    return (
      <div
        className={`recipe-image-fallback ${fallbackClassName}`}
        role="img"
        aria-label={`${alt} photo unavailable. ${reason || "No verified photo is available yet."}`}
        style={{ "--recipe-hue": `${hue}deg` }}
      >
        <span className="recipe-image-fallback-emoji" aria-hidden="true">{emoji}</span>
        <span className="recipe-image-fallback-title">{alt}</span>
        <span className="recipe-image-fallback-status">Photo not verified yet</span>
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      className={className}
      loading={loading}
      decoding="async"
      onError={() => setFailedSrc(src)}
    />
  );
}
