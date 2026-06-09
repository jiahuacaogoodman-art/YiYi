import { Button, Form, Input, InputNumber, Modal, Select, Space, Switch, Table, Tag, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { Plus, Wand2 } from "lucide-react";
import { examApi, questionApi, taxonomyApi } from "../../api/client";
import type { Exam, Question, Subject } from "../../types/domain";
import { shortDate, statusLabel, truncate } from "../../utils/format";

export function ExamsManagePage() {
  const [items, setItems] = useState<Exam[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [editing, setEditing] = useState<Exam | null | "manual" | "auto">(null);
  const [form] = Form.useForm();

  const load = async () => {
    const data = await examApi.adminList({ page_size: 100 });
    setItems(data.items);
  };

  useEffect(() => {
    Promise.all([
      taxonomyApi.subjects({ page_size: 200 }),
      questionApi.list({ page_size: 200, status: "published" }),
      examApi.adminList({ page_size: 100 }),
    ]).then(([subjectData, questionData, examData]) => {
      setSubjects(subjectData.items);
      setQuestions(questionData.items);
      setItems(examData.items);
    });
  }, []);

  const openManual = (record?: Exam) => {
    setEditing(record || "manual");
    form.setFieldsValue(
      record || {
        name: "",
        exam_type: "mock",
        total_score: 100,
        pass_score: 60,
        duration_minutes: 60,
        status: "draft",
        is_public: false,
        question_ids: [],
      },
    );
  };

  const openAuto = () => {
    setEditing("auto");
    form.setFieldsValue({ name: "", question_count: 20, easy_ratio: 0.4, medium_ratio: 0.4, hard_ratio: 0.2, duration_minutes: 60, is_public: false });
  };

  const save = async () => {
    const values = await form.validateFields();
    if (editing === "auto") {
      await examApi.autoGenerate(values);
    } else {
      const selectedIds: number[] = values.question_ids || [];
      const perScore = selectedIds.length ? Number((Number(values.total_score || 100) / selectedIds.length).toFixed(2)) : 5;
      const payload = {
        ...values,
        questions: selectedIds.map((id, index) => ({ question_id: id, score: perScore, sort_order: index + 1 })),
      };
      delete payload.question_ids;
      if (editing && editing !== "manual") await examApi.update(editing.id, payload);
      else await examApi.create(payload);
    }
    message.success("试卷已保存");
    setEditing(null);
    load();
  };

  const publish = async (id: number) => {
    await examApi.publish(id);
    message.success("已发布");
    load();
  };

  const offline = async (id: number) => {
    await examApi.offline(id);
    message.success("已下架");
    load();
  };

  const subjectOptions = subjects.map((item) => ({ label: item.name, value: item.id }));
  const questionOptions = questions.map((item) => ({ label: `#${item.id} ${truncate(item.stem, 48)}`, value: item.id }));

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>套卷/模拟考试管理</Typography.Title>
          <Typography.Text type="secondary">手动组卷或按难度比例自动组卷，发布后学生即可考试。</Typography.Text>
        </div>
        <Space wrap>
          <Button icon={<Wand2 size={16} />} onClick={openAuto}>自动组卷</Button>
          <Button type="primary" icon={<Plus size={16} />} onClick={() => openManual()}>手动创建</Button>
        </Space>
      </div>
      <div className="panel">
        <Table
          rowKey="id"
          dataSource={items}
          columns={[
            { title: "试卷", dataIndex: "name" },
            { title: "科目", dataIndex: "subject_name" },
            { title: "题量", dataIndex: "question_count" },
            { title: "时长", dataIndex: "duration_minutes", render: (value) => `${value} 分钟` },
            { title: "状态", dataIndex: "status", render: (value) => <Tag>{statusLabel[String(value)] || String(value)}</Tag> },
            { title: "创建时间", dataIndex: "created_at", render: (value) => shortDate(value) },
            {
              title: "操作",
              render: (_, row) => (
                <Space>
                  <Button size="small" onClick={() => openManual(row)}>编辑</Button>
                  <Button size="small" type="primary" onClick={() => publish(row.id)}>发布</Button>
                  <Button size="small" danger onClick={() => offline(row.id)}>下架</Button>
                </Space>
              ),
            },
          ]}
        />
      </div>
      <Modal title={editing === "auto" ? "自动组卷" : "编辑试卷"} open={Boolean(editing)} onOk={save} onCancel={() => setEditing(null)} width={760}>
        <Form form={form} layout="vertical">
          <Form.Item label="试卷名称" name="name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item label="科目" name="subject_id" rules={[{ required: true }]}>
            <Select options={subjectOptions} />
          </Form.Item>
          {editing === "auto" ? (
            <Space align="start" wrap>
              <Form.Item label="题量" name="question_count">
                <InputNumber min={1} max={200} />
              </Form.Item>
              <Form.Item label="简单比例" name="easy_ratio">
                <InputNumber min={0} max={1} step={0.1} />
              </Form.Item>
              <Form.Item label="中等比例" name="medium_ratio">
                <InputNumber min={0} max={1} step={0.1} />
              </Form.Item>
              <Form.Item label="困难比例" name="hard_ratio">
                <InputNumber min={0} max={1} step={0.1} />
              </Form.Item>
            </Space>
          ) : (
            <Form.Item label="选择题目" name="question_ids">
              <Select mode="multiple" options={questionOptions} maxTagCount="responsive" />
            </Form.Item>
          )}
          <Space align="start" wrap>
            {editing !== "auto" ? (
              <>
                <Form.Item label="总分" name="total_score">
                  <InputNumber min={1} />
                </Form.Item>
                <Form.Item label="及格分" name="pass_score">
                  <InputNumber min={1} />
                </Form.Item>
              </>
            ) : null}
            <Form.Item label="考试时长" name="duration_minutes">
              <InputNumber min={1} />
            </Form.Item>
            <Form.Item label="公开发布" name="is_public" valuePropName="checked">
              <Switch />
            </Form.Item>
          </Space>
          {editing !== "auto" ? (
            <>
              <Form.Item label="状态" name="status">
                <Select options={[{ label: "草稿", value: "draft" }, { label: "已发布", value: "published" }, { label: "已下架", value: "offline" }]} />
              </Form.Item>
              <Form.Item label="说明" name="description">
                <Input.TextArea rows={3} />
              </Form.Item>
            </>
          ) : null}
        </Form>
      </Modal>
    </div>
  );
}