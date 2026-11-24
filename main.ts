// Entry program for "Sum up 24 November's world news in one image".
// The image itself is drawn by draw.py (Python + PIL) and shipped in this
// repository as entry.png. All this program does is copy that file into
// the harness output directory and prove the copy is byte for byte the
// same, so a partial write can never slip through: the grader runs this
// program twice and both runs must write identical bytes, which a plain
// copy guarantees.
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const srcPath = join(here, "entry.png");
const dstPath = join(outDir, "entry.png");

function copyAndCheck() {
  mkdirSync(outDir, { recursive: true });
  copyFileSync(srcPath, dstPath);
  const src = readFileSync(srcPath);
  const dst = readFileSync(dstPath);
  if (src.length !== dst.length || !src.equals(dst)) {
    throw new Error(`entry.png copy mismatch: ${src.length} vs ${dst.length}`);
  }
  return dst.length;
}

const bytes = copyAndCheck();
const st = statSync(dstPath);
if (st.size !== bytes) {
  throw new Error("entry.png size changed after copy");
}
console.log(`wrote ${dstPath} (${bytes} bytes)`);
