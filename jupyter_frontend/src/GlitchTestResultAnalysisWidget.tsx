import {createRender} from "@anywidget/react";
import React from "react";
import GlitchTestResultAnalysis from "@/components/glitch-test/GlitchTestResultAnalysis.tsx";

const render = createRender(() => {

    return (
        <GlitchTestResultAnalysis/>
    );
});

export default {render};
