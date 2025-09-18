import {useModel, useModelState} from "@anywidget/react";
import {ConnectionProps} from "@/components/Connection.tsx";

export function useConnectionStates(): Omit<ConnectionProps, "disabled"> {
  const model = useModel();

  const [uri, setUri] = useModelState<string>("uri");
  const [connectStatus] = useModelState<boolean>("connect_status");

  const connect = () => {
    model.send({source: "connectButton", event: "onClick", args: {action: "connect"}})
  }

  const disconnect = () => {
    model.send({source: "connectButton", event: "onClick", args: {action: "disconnect"}});
  }

  return {
    uri: uri,
    onUriChanged: setUri,
    connected: connectStatus,
    connect: connect,
    disconnect: disconnect
  };
}