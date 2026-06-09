import { Form, Input, Select, Table, Tag, Typography } from "antd";
import { useEffect, useState } from "react";
import { adminApi } from "../../api/client";
import type { QueryParams } from "../../api/client";
import { shortDate } from "../../utils/format";

export function LogsPage() {
  const [items, setItems] = useState<Array<Record<string, unknown>>>([]);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState<QueryParams>({ page: 1, page_size: 20 });

  useEffect(() => {
    adminApi.logs(filters).then((data) => {
      setItems(data.items);
      setTotal(data.total);
    });
  }, [filters]);

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>操作日志</Typography.Title>
          <Typography.Text type="secondary">追踪后台管理员对题库、用户和系统设置的操作。</Typography.Text>
        </div>
      </div>
      <div className="panel">
        <Form layout="inline" className="filter-form">
          <Form.Item label="动作">
            <Input.Search allowClear onSearch={(action) => setFilters((current) => ({ ...current, action, page: 1 }))} />
          </Form.Item>
          <Form.Item label="对象">
            <Select
              allowClear
              style={{ width: 160 }}
              options={["question", "subject", "chapter", "knowledge_point", "exam", "user", "system_setting"].map((value) => ({ label: value, value }))}
              onChange={(target_type) => setFilters((current) => ({ ...current, target_type, page: 1 }))}
            />
          </Form.Item>
        </Form>
        <Table
          rowKey={(row) => String(row.id)}
          dataSource={items}
          pagination={{ total, current: Number(filters.page), pageSize: Number(filters.page_size), onChange: (page, pageSize) => setFilters((current) => ({ ...current, page, page_size: pageSize })) }}
          columns={[
            { title: "动作", dataIndex: "action", render: (value) => <Tag>{String(value)}</Tag> },
            { title: "对象", dataIndex: "target_type" },
            { title: "对象 ID", dataIndex: "target_id" },
            { title: "摘要", dataIndex: "summary" },
            { title: "时间", dataIndex: "created_at", render: (value) => shortDate(String(value)) },
          ]}
        />
      </div>
    </div>
  );
}