import { Button, Form, Input, Modal, Select, Space, Table, Tag, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { adminApi } from "../../api/client";
import type { QueryParams } from "../../api/client";
import type { Feedback } from "../../types/domain";
import { shortDate, statusLabel } from "../../utils/format";

export function FeedbackManagePage() {
  const [items, setItems] = useState<Feedback[]>([]);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState<QueryParams>({ page: 1, page_size: 20 });
  const [editing, setEditing] = useState<Feedback | null>(null);
  const [form] = Form.useForm();

  const load = async () => {
    const data = await adminApi.feedback(filters);
    setItems(data.items);
    setTotal(data.total);
  };

  useEffect(() => {
    load();
  }, [filters]);

  const save = async () => {
    if (!editing) return;
    const values = await form.validateFields();
    await adminApi.updateFeedback(editing.id, values);
    message.success("反馈已处理");
    setEditing(null);
    load();
  };

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>反馈纠错管理</Typography.Title>
          <Typography.Text type="secondary">处理学生提交的题干、答案、解析和分类问题。</Typography.Text>
        </div>
      </div>
      <div className="panel">
        <Form layout="inline" className="filter-form">
          <Form.Item label="状态">
            <Select
              allowClear
              style={{ width: 150 }}
              options={[
                { label: "未处理", value: "pending" },
                { label: "处理中", value: "processing" },
                { label: "已处理", value: "resolved" },
                { label: "已忽略", value: "ignored" },
              ]}
              onChange={(status) => setFilters((current) => ({ ...current, status, page: 1 }))}
            />
          </Form.Item>
          <Form.Item label="题目 ID">
            <Input.Search onSearch={(value) => setFilters((current) => ({ ...current, question_id: value ? Number(value) : undefined, page: 1 }))} />
          </Form.Item>
        </Form>
        <Table
          rowKey="id"
          dataSource={items}
          pagination={{ total, current: Number(filters.page), pageSize: Number(filters.page_size), onChange: (page, pageSize) => setFilters((current) => ({ ...current, page, page_size: pageSize })) }}
          columns={[
            { title: "题目 ID", dataIndex: "question_id", width: 90 },
            { title: "类型", dataIndex: "feedback_type", width: 120 },
            { title: "内容", dataIndex: "content" },
            { title: "状态", dataIndex: "status", width: 110, render: (value) => <Tag>{statusLabel[String(value)] || String(value)}</Tag> },
            { title: "提交时间", dataIndex: "created_at", width: 130, render: (value) => shortDate(value) },
            {
              title: "操作",
              width: 100,
              render: (_, row) => (
                <Button
                  size="small"
                  onClick={() => {
                    setEditing(row);
                    form.setFieldsValue({ status: row.status, handler_note: row.handler_note });
                  }}
                >
                  处理
                </Button>
              ),
            },
          ]}
        />
      </div>
      <Modal title="处理反馈" open={Boolean(editing)} onOk={save} onCancel={() => setEditing(null)}>
        <Form form={form} layout="vertical">
          <Form.Item label="处理状态" name="status" rules={[{ required: true }]}>
            <Select options={[{ label: "处理中", value: "processing" }, { label: "已处理", value: "resolved" }, { label: "已忽略", value: "ignored" }]} />
          </Form.Item>
          <Form.Item label="处理备注" name="handler_note">
            <Input.TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}