import esbuild from "esbuild";

let ctx = await esbuild.context({
  entryPoints: ["src/*Widget.tsx"],
  format: "esm",
  bundle: true,
  outdir: "../src/cracknuts/jupyter/static",
  logLevel: "info",
  sourcemap: "inline",
})

await ctx.watch()