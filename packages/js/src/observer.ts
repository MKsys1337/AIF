// Adaptive Image Format (AIF) — MutationObserver Integration
// Copyright (C) 2026 Markus Köplin
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program. If not, see <https://www.gnu.org/licenses/>.

import type { AIFRenderer } from "./renderer.js";

/**
 * Observe the DOM for newly added `<img>` elements and automatically
 * process them through the AIF renderer.
 *
 * Handles infinite-scroll feeds, lazy-loaded images, and dynamically
 * injected content.
 *
 * @param renderer - An AIFRenderer instance.
 * @param root - The root element to observe (default: `document.body`).
 * @returns A `MutationObserver` instance (call `.disconnect()` to stop).
 */
export function observeImages(
  renderer: AIFRenderer,
  root: Element = document.body
): MutationObserver {
  // Process all existing images
  root.querySelectorAll("img").forEach((img) => {
    renderer.processImage(img as HTMLImageElement);
  });

  // Watch for new images
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      for (const node of mutation.addedNodes) {
        if (node instanceof HTMLImageElement) {
          renderer.processImage(node);
        }
        if (node instanceof HTMLElement) {
          node.querySelectorAll?.("img")?.forEach((img) => {
            renderer.processImage(img as HTMLImageElement);
          });
        }
      }
    }
  });

  observer.observe(root, { childList: true, subtree: true });

  return observer;
}
