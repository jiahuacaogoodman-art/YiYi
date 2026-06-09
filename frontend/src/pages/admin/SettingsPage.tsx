import { Button, Form, Input, Space, Switch, Table, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { adminApi } from "../../api/client";
import type { SystemSetting } from "../../types/domain";

export function SettingsPage() {
  const [items, setItems] = useState<SystemSetting[]>([]);
  const [forms] = Form.useForm();

  const load = async () => {
    const data = await adminApi.settings();
    setItems(data);
    forms.setFieldsValue(
      data.reduce<Record<string, unknown>>((acc, item) => {
        acc[item.key] = { value: item.value, description: item.description, is_public: item.is_public };
        return acc;
      }, {}),
    );
  };

  useEffect(() => {
    load();
  }, []);

  const save = async (key: string) => {
    const values = forms.getFieldValue(key);
    await adminApi.updateSetting(key, values);
    message.success("设置已保存");
    load();
  };

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>系统设置</Typography.Title>
          <Typography.Text type="secondary">维护平台运行配置，修改权限由超级管理员控制。</Typography.Text>
        </div>
      </div>
      <div className="panel">
        <Form form={forms} component={false}>
          <Table
            rowKey="key"
            dataSource={items}
            pagination={false}
            columns={[
              { title: "配置项", dataIndex: "key", width: 210 },
              {
                title: "值",
                render: (_, row) => (
                  <Form.Item name={[row.key, "value"]} noStyle>
                    <Input />
                  </Form.Item>
                ),
              },
              {
                title: "说明",
                render: (_, row) => (
                  <Form.Item name={[row.key, "description"]} noStyle>
                    <Input />
                  </Form.Item>
                ),
              },
              {
                title: "公开",
                width: 90,
                render: (_, row) => (
                  <Form.Item name={[row.key, "is_public"]} valuePropName="checked" noStyle>
                    <Switch />
                  </Form.Item>
                ),
              },
              {
                title: "操作",
                width: 100,
                render: (_, row) => (
                  <Space>
                    <Button size="small" type="primary" onClick={() => save(row.key)}>保存</Button>
                  </Space>
                ),
              },
            ]}
          />
        </Form>
      </div>
    </div>
  );
}