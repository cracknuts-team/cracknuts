import React from "react";
import Connection, {ConnectionPanelProps} from "@/cracker/Connection.tsx";
import GlitchTestPanel, {GlitchTestPanelProps} from "@/GlitchTestPanel.tsx";


interface CrackerG1PanelProps {
  connection: ConnectionPanelProps;
  glitchTestPanel: GlitchTestPanelProps;
}

const CrackerG1Panel: React.FC<CrackerG1PanelProps> = (props) => {
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
      <GlitchTestPanel
        onApply={props.glitchTestPanel.onApply}
      />
    </div>

  );
};

export default CrackerG1Panel;