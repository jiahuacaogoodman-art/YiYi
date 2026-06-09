import { Button, Form, Input, InputNumber, Modal, Select, Space, Switch, Table, Tabs, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { taxonomyApi } from "../../api/client";
import type { Chapter, KnowledgePoint, Subject } from "../../types/domain";

type EditingType = "subject" | "chapter" | "point";
type Editing = { type: EditingType; record?: Subject | Chapter | KnowledgePoint } | null;

export function TaxonomyManagePage() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [points, setPoints] = useState<KnowledgePoint[]>([]);
  const [editing, setEditing] = useState<Editing>(null);
  const [form] = Form.useForm();
  const location = useLocation();
  const navigate = useNavigate();
  const activeTab = location.pathname.includes("chapters")
    ? "chapters"
    : location.pathname.includes("knowledge-points")
      ? "points"
      : "subjects";

  const load = async () => {
    const [subjectData, chapterData, pointData] = await Promise.all([
      taxonomyApi.subjects({ page_size: 200 }),
      taxonomyApi.chapters({ page_size: 200 }),
      taxonomyApi.knowledgePoints({ page_size: 200 }),
    ]);
    setSubjects(subjectData.items);
    setChapters(chapterData.items);
    setPoints(pointData.items);
  };

  useEffect(() => {
    load();
  }, []);

  const open = (type: EditingType, record?: Subject | Chapter | KnowledgePoint) => {
    setEditing({ type, record });
    form.setFieldsValue(record || { is_enabled: true, sort_order: 0, importance_level: "medium" });
  };

  const save = async () => {
    if (!editing) return;
    const values = await form.validateFields();
    const id = editing.record?.id;
    if (editing.type === "subject") {
      id ? await taxonomyApi.updateSubject(id, values) : await taxonomyApi.createSubject(values);
    } else if (editing.type === "chapter") {
      id ? await taxonomyApi.updateChapter(id, values) : await taxonomyApi.createChapter(values);
    } else {
      id ? await taxonomyApi.updateKnowledgePoint(id, values) : await taxonomyApi.createKnowledgePoint(values);
    }
    message.success("已保存");
    setEditing(null);
    load();
  };

  const remove = async (type: EditingType, id: number) => {
    if (type === "subject") await taxonomyApi.deleteSubject(id);
    if (type === "chapter") await taxonomyApi.deleteChapter(id);
    if (type === "point") await taxonomyApi.deleteKnowledgePoint(id);
    message.success("已删除");
    load();
  };

  const subjectOptions = subjects.map((item) => ({ label: item.name, value: item.id }));
  const chapterOptions = chapters.map((item) => ({ label: `${item.subject_name || ""} / ${item.name}`, value: item.id }));

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>分类管理</Typography.Title>
          <Typography.Text type="secondary">维护科目分栏、章节和知识点，让非技术人员也能整理题库结构。</Typography.Text>
        </div>
      </div>
      <Tabs
        className="panel-tabs"
        activeKey={activeTab}
        onChange={(key) => {
          const path = key === "chapters" ? "/admin/chapters" : key === "points" ? "/admin/knowledge-points" : "/admin/subjects";
          navigate(path);
        }}
        items={[
          {
            key: "subjects",
            label: "科目分栏",
            children: (
              <div className="panel">
                <Button type="primary" icon={<Plus size={16} />} onClick={() => open("subject")}>新增科目</Button>
                <Table
                  rowKey="id"
                  dataSource={subjects}
                  columns={[
                    { title: "名称", dataIndex: "name" },
                    { title: "代码", dataIndex: "code" },
                    { title: "题量", dataIndex: "question_count" },
                    { title: "排序", dataIndex: "sort_order" },
                    { title: "启用", dataIndex: "is_enabled", render: (value) => <Switch checked={value} disabled /> },
                    {
                      title: "操作",
                      render: (_, row) => (
                        <Space>
                          <Button size="small" onClick={() => open("subject", row)}>编辑</Button>
                          <Button size="small" danger onClick={() => remove("subject", row.id)}>删除</Button>
                        </Space>
                      ),
                    },
                  ]}
                />
              </div>
            ),
          },
          {
            key: "chapters",
            label: "章节",
            children: (
              <div className="panel">
                <Button type="primary" icon={<Plus size={16} />} onClick={() => open("chapter")}>新增章节</Button>
                <Table
                  rowKey="id"
                  dataSource={chapters}
                  columns={[
                    { title: "章节", dataIndex: "name" },
                    { title: "科目", dataIndex: "subject_name" },
                    { title: "代码", dataIndex: "code" },
                    { title: "题量", dataIndex: "question_count" },
                    { title: "启用", dataIndex: "is_enabled", render: (value) => <Switch checked={value} disabled /> },
                    {
                      title: "操作",
                      render: (_, row) => (
                        <Space>
                          <Button size="small" onClick={() => open("chapter", row)}>编辑</Button>
                          <Button size="small" danger onClick={() => remove("chapter", row.id)}>删除</Button>
                        </Space>
                      ),
                    },
                  ]}
                />
              </div>
            ),
          },
          {
            key: "points",
            label: "知识点",
            children: (
              <div className="panel">
                <Button type="primary" icon={<Plus size={16} />} onClick={() => open("point")}>新增知识点</Button>
                <Table
                  rowKey="id"
                  dataSource={points}
                  columns={[
                    { title: "知识点", dataIndex: "name" },
                    { title: "科目", dataIndex: "subject_name" },
                    { title: "章节", dataIndex: "chapter_name" },
                    { title: "重要度", dataIndex: "importance_level" },
                    { title: "题量", dataIndex: "question_count" },
                    {
                      title: "操作",
                      render: (_, row) => (
                        <Space>
                          <Button size="small" onClick={() => open("point", row)}>编辑</Button>
                          <Button size="small" danger onClick={() => remove("point", row.id)}>删除</Button>
                        </Space>
                      ),
                    },
                  ]}
                />
              </div>
            ),
          },
        ]}
      />
      <Modal title="编辑分类" open={Boolean(editing)} onOk={save} onCancel={() => setEditing(null)} width={620}>
        <Form form={form} layout="vertical">
          {editing?.type !== "subject" ? (
            <Form.Item label="科目" name="subject_id" rules={[{ required: true }]}>
              <Select options={subjectOptions} />
            </Form.Item>
          ) : null}
          {editing?.type === "point" ? (
            <Form.Item label="章节" name="chapter_id" rules={[{ required: true }]}>
              <Select options={chapterOptions} />
            </Form.Item>
          ) : null}
          <Form.Item label="名称" name="name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          {editing?.type !== "point" ? (
            <Form.Item label="代码" name="code" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
          ) : (
            <Form.Item label="标签" name="label">
              <Input />
            </Form.Item>
          )}
          {editing?.type === "point" ? (
            <Form.Item label="重要程度" name="importance_level">
              <Select options={[{ label: "普通", value: "medium" }, { label: "重点", value: "high" }, { label: "基础", value: "low" }]} />
            </Form.Item>
          ) : null}
          <Form.Item label="排序" name="sort_order">
            <InputNumber min={0} />
          </Form.Item>
          <Form.Item label="启用" name="is_enabled" valuePropName="checked">
            <Switch />
          </Form.Item>
          <Form.Item label="描述" name="description">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}