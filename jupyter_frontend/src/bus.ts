import mitt from "mitt"
import {LanguageCode} from "@/components/Configuration.tsx";

export const bus = mitt<{
    dumpConfigCompleted: string,
    changeLanguage: LanguageCode
}>();