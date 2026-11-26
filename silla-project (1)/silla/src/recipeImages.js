import manifest from "./recipeImageManifest.json";

export function getRecipeImageEntry(recipeId) {
  const resolvedId = manifest.aliases[recipeId] || recipeId;
  return manifest.recipes[resolvedId] || null;
}
