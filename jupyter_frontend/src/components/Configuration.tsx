import React, {useEffect} from "react";
import {Button, Form, Tooltip, Upload} from "antd";
import {BlockOutlined, ExportOutlined, ImportOutlined, SaveOutlined, ThunderboltOutlined} from "@ant-design/icons";
import {FormattedMessage, useIntl} from "react-intl";
import {bus} from "@/bus.ts";

type LanguageCode = 'zh' | 'en';

interface ConfigurationProps {
    panelConfigDifferentFromCrackerConfig: boolean;
    readConfig: () => void;
    writeConfig: () => void;
    loadConfig: (config: string) => void;
    dumpConfig: () => void;
    saveConfig: () => void;
}

const Configuration: React.FC<ConfigurationProps> = ({
                                                         panelConfigDifferentFromCrackerConfig,
                                                         readConfig,
                                                         writeConfig,
                                                         loadConfig,
                                                         dumpConfig,
                                                         saveConfig,
                                                     }) => {
    const intl = useIntl();

    const changeLanguage = () => {
        if (intl.locale === 'zh') {
            bus.emit("changeLanguage", 'en')
        } else {
            bus.emit('changeLanguage', 'zh')
        }
    };

    const dumpConfigCompleted = (config: string) => {
        const blob = new Blob([config], {type: "text/plain"});
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "config.json";
        link.click();
        URL.revokeObjectURL(link.href);
    };

    const uploadProp = {
        maxCount: 1,
        showUploadList: false,
        // @ts-expect-error option type ignore
        customRequest: (options) => {
            console.info(options);
            const reader = new FileReader();
            reader.readAsText(options.file);
            reader.onload = () => {
                loadConfig(JSON.parse(String(reader.result)));
            };
            options.onSuccess();
        },
    };

    useEffect(() => {
        bus.on("dumpConfigCompleted", dumpConfigCompleted);

        return () => {
            bus.off("dumpConfigCompleted", dumpConfigCompleted)
        };
    }, []);

    return (
        <Form layout={"inline"}>
            <Form.Item>
                <Tooltip
                    title={panelConfigDifferentFromCrackerConfig ? intl.formatMessage({id: "cracknuts.config.write.tooltip.different"}) : intl.formatMessage({id: "cracknuts.config.write.tooltip"})}>
                    <Button icon={<ThunderboltOutlined/>} size={"small"} onClick={writeConfig}
                            color={panelConfigDifferentFromCrackerConfig ? "danger" : "primary"} variant="solid">
                        <FormattedMessage id={"cracknuts.config.write"}/>
                    </Button>
                </Tooltip>
            </Form.Item>
            <Form.Item>
                <Tooltip title={intl.formatMessage({id: "cracknuts.config.read.tooltip"})}>
                    <Button icon={<BlockOutlined/>} size={"small"} onClick={readConfig} type="primary">
                        <FormattedMessage id={"cracknuts.config.read"}/>
                    </Button>
                </Tooltip>
            </Form.Item>
            <Form.Item>
                <Tooltip title={intl.formatMessage({id: "cracknuts.config.save.tooltip"})}>
                    <Button icon={<SaveOutlined/>} size={"small"} onClick={saveConfig} type="primary">
                        <FormattedMessage id={"cracknuts.config.save"}/>
                    </Button>
                </Tooltip>
            </Form.Item>
            <Form.Item>
                <Tooltip title={intl.formatMessage({id: "cracknuts.config.load.tooltip"})}>
                    <Upload {...uploadProp}>
                        <Button icon={<ImportOutlined/>} size={"small"} type="primary">
                            <FormattedMessage id={"cracknuts.config.load"}/>
                        </Button>
                    </Upload>
                </Tooltip>
            </Form.Item>
            <Form.Item>
                <Tooltip title={intl.formatMessage({id: "cracknuts.config.dump.tooltip"})}>
                    <Button icon={<ExportOutlined/>} size={"small"} onClick={dumpConfig} type="primary">
                        <FormattedMessage id={"cracknuts.config.dump"}/>
                    </Button>
                </Tooltip>
            </Form.Item>
            <Form.Item>
                <Button size={"small"} variant="text" color="default" onClick={changeLanguage}>
                    <span style={{fontSize: '0.8em', width: 13, textAlign: 'center'}}>{intl.formatMessage({id: "language"})}</span>
                </Button>
            </Form.Item>
        </Form>
    );
};

export default Configuration;
export type {ConfigurationProps, LanguageCode};