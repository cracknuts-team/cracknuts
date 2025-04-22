import {Breadcrumb, Button, Input, Layout, List, Modal, Space, Spin,} from 'antd';
import React, {useState} from 'react';
import './FileSelector.css';
import {FileOutlined, FolderOutlined} from '@ant-design/icons';


interface DirectoryListNode {
  name: string;
  type: "folder" | "file";
}

interface DefaultDirectoryInfo {
  partitions: string[],
  path: string,
  directoryList: DirectoryListNode[]
}

interface FileSelectorProps {
  getDefaultDirectoryInfo: (initDirectory: string | null | undefined) => Promise<DefaultDirectoryInfo>,
  getDirectoryList: (path: string) => Promise<DirectoryListNode[]>;
  selectedPathChanged: (path: string) => void;
  selectedPath?: string;
  size?: "small" | "middle" | "large";
}


const FileSelector: React.FC<FileSelectorProps> = ({
                                                     getDefaultDirectoryInfo,
                                                     getDirectoryList,
                                                     selectedPath,
                                                     selectedPathChanged,
                                                     size = "middle"
                                                   }) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [breadcrumbPaths, _setBreadcrumbPath] = useState<string[]>([]);
  const setBreadcrumbPath = (path: string) => {
    const pathParts = path.split("/").filter(Boolean);
    if (path.charAt(1) !== ":") {
      // Uinix-like path
      pathParts.unshift("/")
    }
    _setBreadcrumbPath(pathParts);
  };
  const [partitions, setPartitions] = useState<string[]>([]);
  const [directoryList, setDirectoryList] = useState<DirectoryListNode[]>([]);
  const [selectedItem, setSelectedItem] = useState<string | null>(null);
  const [_selectedPath, setSelectedPath] = useState<string | undefined>(selectedPath);

  const handlePathChange = async (path: string) => {
    setBreadcrumbPath(path);
    const list = await getDirectoryList(path);
    setDirectoryList(list);
    setSelectedItem(null);
  };

  const openModal = async () => {
    setModalOpen(true);
    setLoading(true);
    const defaultDirectoryInfo = await getDefaultDirectoryInfo(selectedPath);
    if (defaultDirectoryInfo) {
      setPartitions(defaultDirectoryInfo.partitions);
      setBreadcrumbPath(defaultDirectoryInfo.path);
      setDirectoryList(defaultDirectoryInfo.directoryList);
    }
    setLoading(false);
  };

  const handleOk = () => {
    let path = breadcrumbPaths.join("/");
    if (path.substring(0, 2) === "//") {
      path = path.substring(1, path.length);
    }
    if (selectedItem) {
      if (!path.endsWith("/")) {
        path += "/"
      }
      path += selectedItem;
    }
    setSelectedPath(path)
    selectedPathChanged(path);
    setModalOpen(false);
  }

  return (
    <div>
      <Space.Compact>
        <Input value={_selectedPath} readOnly size={size}/>
        <Button onClick={openModal} size={size}>选择路径</Button>
      </Space.Compact>
      <Modal open={modalOpen} onCancel={() => {
        setModalOpen(false)
      }} title="选择文件位置" width={800} onOk={handleOk} destroyOnClose>
        <Spin spinning={loading}>
          <Layout style={{height: 400, border: "1px solid #d9d9d9"}}>
            <Layout.Sider width={120}
                          style={{
                            background: "#fff",
                            padding: "8px",
                            borderRight: "1px solid #d9d9d9",
                          }}>
              <div style={{fontWeight: "bold", marginBottom: "8px"}}>磁盘</div>
              {partitions.map((partition) => (
                <div
                  key={partition}
                  onClick={() => handlePathChange(partition)}
                  className="partition-item"
                >
                  {partition}
                </div>
              ))}
            </Layout.Sider>
            <Layout.Content style={{background: "#fff", display: "flex", flexDirection: "column"}}>
              <div
                style={{
                  padding: "8px 12px",
                  borderBottom: "1px solid #d9d9d9",
                  background: "#fafafa",
                }}
              >
                <Breadcrumb items={breadcrumbPaths.map((part, index) => {
                  const path = breadcrumbPaths.slice(0, index + 1).join("/");
                  return {
                    key: path,
                    title: (
                      <span
                        style={{cursor: "pointer"}}
                        onClick={() => handlePathChange(path)}
                      >
                        {part == "/" ? "根目录" : part}
                      </span>
                    ),
                  };
                })}/>
              </div>
              <div
                style={{
                  flex: 1,
                  padding: "8px 12px",
                  borderLeft: "1px solid #f0f0f0",
                  borderRight: "1px solid #f0f0f0",
                  borderTop: "1px solid #f0f0f0",
                  overflowY: "auto",
                }}
              >
                <List
                  size="small"
                  dataSource={directoryList}
                  renderItem={(item: DirectoryListNode) => (
                    <List.Item
                      style={{
                        cursor: "pointer",
                        backgroundColor:
                          selectedItem === item.name ? "#e6f7ff" : "transparent",
                      }}
                      onClick={() => {
                        setSelectedItem(item.name); // 设置选中项
                      }}
                      onDoubleClick={() => {
                        if (item.type === "folder") {
                          let path = breadcrumbPaths.join("/");
                          if (path.substring(0, 2) === "//") {
                            path = path.substring(1, path.length);
                          }
                          if (!path.endsWith("/")) {
                            path += "/"
                          }
                          path += item.name;
                          handlePathChange(path);
                        }
                      }}
                    >
                      <List.Item.Meta
                        avatar={
                          item.type === "folder" ? (
                            <FolderOutlined
                              style={{fontSize: 18, color: "#1890ff"}}
                            />
                          ) : (
                            <FileOutlined
                              style={{fontSize: 18, color: "#faad14"}}
                            />
                          )
                        }
                        title={item.name}
                      />
                    </List.Item>
                  )}
                />
              </div>
            </Layout.Content>
          </Layout>
        </Spin>
      </Modal>
    </div>
  );
}

export default FileSelector;

export type {DirectoryListNode, DefaultDirectoryInfo};
