import React, {ChangeEvent, useEffect, useState} from "react";
import {Button, Input, Space} from "antd";
import {useIntl} from "react-intl";


interface ConnectionProps {
  uri: string,
  onUriChanged: (uri: string) => void;
  connect: () => void;
  disconnect: () => void;
  connected: boolean;
  disabled: boolean;
}

const Connection: React.FC<ConnectionProps> = ({
                                                 uri,
                                                 onUriChanged,
                                                 connect,
                                                 disconnect,
                                                 connected = false,
                                                 disabled = false
                                               }) => {

  const [buttonBusy, setButtonBusy] = useState<boolean>(false);

  const intl = useIntl();

  const getUri = () => {
    if (uri) {
      return uri.replace("cnp://", "");
    } else {
      return "";
    }
  };

  function connectButtonOnClick() {
    if (connected) {
      disconnect();
    } else {
      setButtonBusy(true);
      connect();
    }
  }

  useEffect(() => {
    setButtonBusy(false);
  }, [connected]);

  return (
    <Space size={"large"} style={{paddingTop: "5px", paddingBottom: "5px"}}>
      <Space.Compact style={{maxWidth: "18em", minWidth: "18em"}} size={"small"}>
        <Input
          addonBefore="cnp://"
          value={getUri()}
          onChange={(e: ChangeEvent<HTMLInputElement>) => {
            onUriChanged("cnp://" + e.target.value);
          }}
        />
        <Button
          type="primary"
          onClick={connectButtonOnClick}
          loading={buttonBusy}
          disabled={disabled}>
          {connected ? intl.formatMessage({id: 'cracker.disconnect'}) : intl.formatMessage({id: 'cracker.connect'})}
        </Button>
      </Space.Compact>
    </Space>
  );
};

export default Connection;
export type {ConnectionProps};