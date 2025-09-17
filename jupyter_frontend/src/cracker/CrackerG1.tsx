import React from "react";
import Connection, {ConnectionProps} from "@/cracker/Connection.tsx";
import G1Config, {G1ConfigProps} from "@/cracker/config/G1Config.tsx";


interface CrackerG1PanelProps {
  connection: ConnectionProps;
  config: G1ConfigProps;
}

const CrackerG1: React.FC<CrackerG1PanelProps> = (props) => {
  return (
    <div>
      <Connection
        uri={props.connection.uri}
        connect={props.connection.connect}
        connected={props.connection.connected}
        onUriChanged={props.connection.onUriChanged}
        disconnect={props.connection.disconnect}
        disabled={props.connection.disabled}
      />
      <G1Config common={props.config.common} glitchTest={props.config.glitchTest} />
    </div>

  );
};

export default CrackerG1;