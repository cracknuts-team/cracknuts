import esbuild from "esbuild";

await esbuild.build({
  entryPoints: ["src/*Widget.tsx"],
  format: "esm",
  minify: true,
  bundle: true,
  outdir: "../src/cracknuts/jupyter/static",
  define: {
    "process.env.NODE_ENV": "\"production\""
  },
  logLevel: "info",
}).catch(() => process.exit(1));
