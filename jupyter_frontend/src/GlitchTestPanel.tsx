import {Button, Col, InputNumber, Radio, Row, Select, SelectProps, Table} from "antd"
import React, {useState} from "react";
import {CheckboxChangeEvent} from "antd/es/checkbox";
import {useIntl} from "react-intl";

type GlitchTestModelSelectProps = {
  value?: number;
  onChange?: SelectProps["onChange"];
};

const GlitchTestModelSelect: React.FC<GlitchTestModelSelectProps> = ({value, onChange}) => {
  const intl = useIntl();
  return (
    <Select size={"small"}
            value={value ?? 0}
            style={{minWidth: 100}}
            onChange={onChange}
            options={[
              {value: 0, label: intl.formatMessage({id: "cracker.config.glitchTest.mode.increase"})},
              {value: 1, label: intl.formatMessage({id: "cracker.config.glitchTest.mode.decrease"})},
              {value: 2, label: intl.formatMessage({id: "cracker.config.glitchTest.mode.random"})},
              {value: 3, label: intl.formatMessage({id: "cracker.config.glitchTest.mode.fixed"})},
            ]}
    />
  );
};

type GlitchGenerateParam = {
  mode: 0 | 1 | 2 | 3; // 0: Increase, 1: Decrease, 2: Random, 3: Fixed
  start: number;
  end: number;
  step: number;
  count: number;
};

type GlitchGenerateParamProps = {
  prop: string;
  param: GlitchGenerateParam;
  unit: string;
  min?: number;
  max?: number;
}

interface GlitchTestPropPanelData {
  data: GlitchGenerateParamProps[];
  setData: React.Dispatch<React.SetStateAction<GlitchGenerateParamProps[]>>;
}

const GlitchTestPropPanel: React.FC<GlitchTestPropPanelData> = ({data, setData}) => {

  const intl = useIntl();
  const updateField = (
    index: number,
    field: keyof GlitchGenerateParam,
    value: number
  ) => {
    setData((prev) => {
      const copy = [...prev];
      copy[index] = {
        ...copy[index],
        param: {
          ...copy[index].param,
          [field]: value,
        },
      };
      return copy;
    });
  };

  const getPrecision = (step: number): number => {
    const stepStr = step.toString();
    if (stepStr.includes('.')) {
      return stepStr.split('.')[1].length;
    }
    return 0;
  }


  const columns = [{
    title: '',
    dataIndex: 'prop',
    key: 'prop',
  }, {
    title: intl.formatMessage({id: "cracker.config.glitchTest.mode"}),
    dataIndex: 'mode',
    key: 'mode',
  }, {
    title: intl.formatMessage({id: "cracker.config.glitchTest.start"}),
    dataIndex: 'start',
    key: 'start',
  }, {
    title: intl.formatMessage({id: "cracker.config.glitchTest.end"}),
    dataIndex: 'end',
    key: 'end',
  }, {
    title: intl.formatMessage({id: "cracker.config.glitchTest.step"}),
    dataIndex: 'step',
    key: 'step',
  }, {
    title: intl.formatMessage({id: "cracker.config.glitchTest.count"}),
    dataIndex: 'count',
    key: 'count',
  }];

  const dataSource = data.map((item, index) => {
    return {
      key: index,
      prop: item.prop,
      mode: <GlitchTestModelSelect
        value={item.param.mode}
        onChange={(val) => {
          updateField(index, 'mode', val as number)
        }}/>,
      start: (
        <InputNumber
          size={"small"}
          min={item.min ?? 0}
          max={Math.min(item.max ?? 255, item.param.end)}
          precision={getPrecision(item.param.step)}
          step={item.param.step}
          changeOnWheel
          value={item.param.start}
          onChange={(val) => {
            updateField(index, 'start', val as number)
          }}
        />
      ),
      end: (
        <InputNumber
          size={"small"}
          min={Math.max(item.min ?? 0, item.param.start)}
          max={item.max ?? 255}
          precision={getPrecision(item.param.step)}
          step={item.param.step}
          changeOnWheel
          value={item.param.end}
          onChange={(val) => {
            updateField(index, 'end', val as number)
          }}
        />
      ),
      step: (
        <InputNumber
          size={"small"}
          min={0.1}
          max={item.max ?? 255}
          precision={getPrecision(item.param.step)}
          step={item.param.step}
          changeOnWheel
          value={item.param.step}
          onChange={(val) => {
            updateField(index, 'step', val as number)
          }}
        />
      ),
      count: (
        <InputNumber
          size={"small"}
          min={1}
          precision={0}
          step={1}
          changeOnWheel
          value={item.param.count}
          onChange={(val) => {
            updateField(index, 'count', val as number)
          }}
        />
      ),
    };
  });

  return (
    <Table
      columns={columns}
      dataSource={dataSource}
      size={"small"}
      pagination={false}
    />
  );
};

interface GlitchTestPanelOnApplyParam {
  type: 'vcc' | 'gnd' | 'clock';
  data: GlitchGenerateParamProps[];
}

interface GlitchTestPanelProps {
  onApply: (params: GlitchTestPanelOnApplyParam) => void;
}

const GlitchTestPanel: React.FC<GlitchTestPanelProps> = ({onApply}) => {
  const [vccGlitchParamGenerators, setVccGlitchParamGenerators] = useState<GlitchGenerateParamProps[]>([{
    prop: 'normal',
    param: {
      mode: 3,
      start: 3.5,
      end: 3.5,
      step: 0.1,
      count: 1,
    },
    min: 1.5,
    max: 5.0,
    unit: 'v',
  }, {
    prop: 'glitch',
    param: {
      mode: 3,
      start: 1.5,
      end: 1.5,
      step: 0.1,
      count: 1,
    },
    min: 1.5,
    max: 5.0,
    unit: 'v',
  }, {
    prop: 'wait',
    param: {
      mode: 3,
      start: 0,
      end: 0,
      step: 1,
      count: 1,
    },
    min: 0,
    max: Number.MAX_VALUE,
    unit: '5ns',
  }, {
    prop: 'repeat',
    param: {
      mode: 3,
      start: 1,
      end: 1,
      step: 1,
      count: 1,
    },
    min: 1,
    max: Number.MAX_VALUE,
    unit: 'times',
  }, {
    prop: 'interval',
    param: {
      mode: 3,
      start: 1,
      end: 1,
      step: 1,
      count: 1,
    },
    min: 1,
    max: Number.MAX_VALUE,
    unit: '5ns',
  }]);
  const [gndGlitchParamGenerators, setGndGlitchParamGenerators] = useState<GlitchGenerateParamProps[]>([{
    prop: 'normal',
    param: {
      mode: 3,
      start: 0,
      end: 0,
      step: 0.1,
      count: 1,
    },
    min: 0,
    max: 5.0,
    unit: 'v',
  }, {
    prop: 'glitch',
    param: {
      mode: 3,
      start: 1.5,
      end: 1.5,
      step: 0.1,
      count: 1,
    },
    min: 0,
    max: 5.0,
    unit: 'v',
  }, {
    prop: 'wait',
    param: {
      mode: 3,
      start: 0,
      end: 0,
      step: 1,
      count: 1,
    },
    min: 0,
    max: Number.MAX_VALUE,
    unit: '5ns',
  }, {
    prop: 'repeat',
    param: {
      mode: 3,
      start: 1,
      end: 1,
      step: 1,
      count: 1,
    },
    min: 1,
    max: Number.MAX_VALUE,
    unit: 'times',
  }, {
    prop: 'interval',
    param: {
      mode: 3,
      start: 1,
      end: 1,
      step: 1,
      count: 1,
    },
    min: 1,
    max: Number.MAX_VALUE,
    unit: '5ns',
  }]);
  const [clockGlitchParamGenerators, setClockGlitchParamGenerators] = useState<GlitchGenerateParamProps[]>([{
    prop: 'normal',
    param: {
      mode: 0,
      start: 0,
      end: 255,
      step: 1,
      count: 10,
    },
    min: 0,
    max: 255,
    unit: 'MHz',
  }, {
    prop: 'wait',
    param: {
      mode: 0,
      start: 0,
      end: 255,
      step: 1,
      count: 10,
    },
    min: 0,
    max: 255,
    unit: 'MHz',
  }]);

  type GlitchType = 'vcc' | 'gnd' | 'clock';

  const [selected, setSelected] = useState<GlitchType>('vcc');

  const dataMap: Record<GlitchType, {
    data: GlitchGenerateParamProps[];
    setData: React.Dispatch<React.SetStateAction<GlitchGenerateParamProps[]>>;
  }> = {
    vcc: {data: vccGlitchParamGenerators, setData: setVccGlitchParamGenerators},
    gnd: {data: gndGlitchParamGenerators, setData: setGndGlitchParamGenerators},
    clock: {data: clockGlitchParamGenerators, setData: setClockGlitchParamGenerators},
  };

  return (
    <Row>
      <Col span={24}>
        <Row style={{marginBottom: 8}} gutter={8}>
          <Col flex={"auto"}>
            <Radio.Group
              value={selected}
              buttonStyle="solid"
              onChange={(e: CheckboxChangeEvent) => {
                setSelected(e.target.value as 'vcc' | 'gnd' | 'clock');
              }}
              size={"small"}
            >
              <Radio.Button value={"vcc"}>
                VCC
              </Radio.Button>
              <Radio.Button value={"gnd"}>
                GND
              </Radio.Button>
              <Radio.Button value={"clock"}>
                CLOCK
              </Radio.Button>
            </Radio.Group>
          </Col>
          <Col style={{marginLeft: 'auto'}}>
            <Button size={"small"} onClick={() => {
              onApply({type: selected, data: dataMap[selected].data})
            }}>Apply</Button>
          </Col>
        </Row>
        <Row>
          <Col span={24}>
            <GlitchTestPropPanel
              data={dataMap[selected].data}
              setData={dataMap[selected].setData}
            />
          </Col>
        </Row>
      </Col>
    </Row>
  );
};

export type {GlitchTestPanelProps, GlitchTestPanelOnApplyParam};
export default GlitchTestPanel;