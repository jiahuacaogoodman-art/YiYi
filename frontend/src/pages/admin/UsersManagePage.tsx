import { Button, Form, Input, Modal, Select, Space, Switch, Table, Tag, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { adminApi } from "../../api/client";
import type { QueryParams } from "../../api/client";
import type { User } from "../../types/domain";
import { percent, shortDate } from "../../utils/format";

export function UsersManagePage() {
  const [items, setItems] = useState<User[]>([]);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState<QueryParams>({ page: 1, page_size: 20 });
  const [createOpen, setCreateOpen] = useState(false);
  const [passwordUser, setPasswordUser] = useState<User | null>(null);
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();

  const load = async () => {
    const data = await adminApi.users(filters);
    setItems(data.items);
    setTotal(data.total);
  };

  useEffect(() => {
    load();
  }, [filters]);

  const create = async () => {
    const values = await form.validateFields();
    await adminApi.createAdminUser(values);
    message.success("管理员账号已创建");
    setCreateOpen(false);
    form.resetFields();
    load();
  };

  const status = async (user: User, isActive: boolean) => {
    await adminApi.updateUserStatus(user.id, { is_active: isActive });
    message.success("用户状态已更新");
    load();
  };

  const resetPassword = async () => {
    if (!passwordUser) return;
    const values = await passwordForm.validateFields();
    await adminApi.resetPassword(passwordUser.id, values);
    message.success("密码已重置");
    setPasswordUser(null);
    passwordForm.resetFields();
  };

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>用户管理</Typography.Title>
          <Typography.Text type="secondary">查看学生学习数据，启用禁用账号，超级管理员可创建后台账号。</Typography.Text>
        </div>
        <Button type="primary" icon={<Plus size={16} />} onClick={() => setCreateOpen(true)}>创建管理员</Button>
      </div>
      <div className="panel">
        <Form layout="inline" className="filter-form">
          <Form.Item label="关键词">
            <Input.Search allowClear onSearch={(keyword) => setFilters((current) => ({ ...current, keyword, page: 1 }))} />
          </Form.Item>
          <Form.Item label="角色">
            <Select
              allowClear
              style={{ width: 150 }}
              options={[
                { label: "学生", value: "student" },
                { label: "管理员", value: "admin" },
                { label: "超级管理员", value: "super_admin" },
              ]}
              onChange={(role) => setFilters((current) => ({ ...current, role, page: 1 }))}
            />
          </Form.Item>
          <Form.Item label="状态">
            <Select
              allowClear
              style={{ width: 130 }}
              options={[{ label: "启用", value: true }, { label: "禁用", value: false }]}
              onChange={(is_active) => setFilters((current) => ({ ...current, is_active, page: 1 }))}
            />
          </Form.Item>
        </Form>
        <Table
          rowKey="id"
          dataSource={items}
          pagination={{ total, current: Number(filters.page), pageSize: Number(filters.page_size), onChange: (page, pageSize) => setFilters((current) => ({ ...current, page, page_size: pageSize })) }}
          columns={[
            { title: "用户名", dataIndex: "username" },
            { title: "昵称", dataIndex: "nickname" },
            { title: "角色", dataIndex: ["role", "label"], render: (_, row) => <Tag>{row.role?.label || row.role?.name}</Tag> },
            { title: "刷题", dataIndex: "total_answers" },
            { title: "正确率", dataIndex: "correct_rate", render: (value) => percent(value) },
            { title: "错题", dataIndex: "wrong_count" },
            { title: "收藏", dataIndex: "favorite_count" },
            { title: "状态", dataIndex: "is_active", render: (value, row) => <Switch checked={value} onChange={(checked) => status(row, checked)} /> },
            { title: "注册时间", dataIndex: "created_at", render: (value) => shortDate(value) },
            {
              title: "操作",
              render: (_, row) => <Button size="small" onClick={() => setPasswordUser(row)}>重置密码</Button>,
            },
          ]}
        />
      </div>
      <Modal title="创建管理员账号" open={createOpen} onOk={create} onCancel={() => setCreateOpen(false)}>
        <Form form={form} layout="vertical" initialValues={{ role: "admin" }}>
          <Form.Item label="用户名" name="username" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="密码" name="password" rules={[{ required: true, min: 6 }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item label="昵称" name="nickname">
            <Input />
          </Form.Item>
          <Form.Item label="角色" name="role">
            <Select options={[{ label: "管理员", value: "admin" }, { label: "超级管理员", value: "super_admin" }]} />
          </Form.Item>
        </Form>
      </Modal>
      <Modal title={`重置密码：${passwordUser?.username || ""}`} open={Boolean(passwordUser)} onOk={resetPassword} onCancel={() => setPasswordUser(null)}>
        <Form form={passwordForm} layout="vertical">
          <Form.Item label="新密码" name="new_password" rules={[{ required: true, min: 6 }]}>
            <Input.Password />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}