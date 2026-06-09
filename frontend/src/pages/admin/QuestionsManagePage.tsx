import {
  Button,
  Form,
  Input,
  InputNumber,
  Modal,
  Select,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
  Upload,
  message,
} from "antd";
import { useEffect, useState } from "react";
import { Plus, Search } from "lucide-react";
import { questionApi, taxonomyApi } from "../../api/client";
import type { QueryParams } from "../../api/client";
import type { Chapter, KnowledgePoint, Question, QuestionOption, Subject } from "../../types/domain";
import { difficultyLabel, questionTypeLabel, shortDate, statusLabel, truncate } from "../../utils/format";

const defaultOptions: QuestionOption[] = ["A", "B", "C", "D"].map((key, index) => ({
  option_key: key,
  content: "",
  sort_order: index + 1,
}));

export function QuestionsManagePage() {
  const [items, setItems] = useState<Question[]>([]);
  const [total, setTotal] = useState(0);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [points, setPoints] = useState<KnowledgePoint[]>([]);
  const [filters, setFilters] = useState<QueryParams>({ page: 1, page_size: 20, include_deleted: false });
  const [selected, setSelected] = useState<React.Key[]>([]);
  const [editing, setEditing] = useState<Question | null | "new">(null);
  const [duplicateOpen, setDuplicateOpen] = useState(false);
  const [duplicates, setDuplicates] = useState<Array<Record<string, unknown>>>([]);
  const [batchDifficultyOpen, setBatchDifficultyOpen] = useState(false);
  const [batchTagsOpen, setBatchTagsOpen] = useState(false);
  const [form] = Form.useForm();
  const [duplicateForm] = Form.useForm();
  const [batchForm] = Form.useForm();

  const load = async () => {
    const data = await questionApi.list(filters);
    setItems(data.items);
    setTotal(data.total);
  };

  useEffect(() => {
    Promise.all([
      taxonomyApi.subjects({ page_size: 200 }),
      taxonomyApi.chapters({ page_size: 200 }),
      taxonomyApi.knowledgePoints({ page_size: 200 }),
    ]).then(([subjectData, chapterData, pointData]) => {
      setSubjects(subjectData.items);
      setChapters(chapterData.items);
      setPoints(pointData.items);
    });
  }, []);

  useEffect(() => {
    load();
  }, [filters]);

  const open = (record?: Question) => {
    setEditing(record || "new");
    form.setFieldsValue(
      record || {
        question_type: "single_choice",
        difficulty: "medium",
        importance: "normal",
        source: "self_built",
        status: "draft",
        options: defaultOptions,
        tags_text: "",
        has_image: false,
      },
    );
    if (record) {
      form.setFieldsValue({ tags_text: record.tags?.join(",") || "" });
    }
  };

  const save = async () => {
    const values = await form.validateFields();
    const payload = {
      ...values,
      tags: String(values.tags_text || "")
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      options: (values.options || []).filter((item: QuestionOption) => item.option_key && item.content),
    };
    delete payload.tags_text;
    if (editing && editing !== "new") {
      await questionApi.update(editing.id, payload);
    } else {
      await questionApi.create(payload);
    }
    message.success("题目已保存");
    setEditing(null);
    load();
  };

  const batch = async (action: string) => {
    if (!selected.length) {
      message.info("请先选择题目");
      return;
    }
    await questionApi.batch({ ids: selected.map(Number), action });
    message.success("批量操作完成");
    setSelected([]);
    load();
  };

  const batchWithValues = async (action: string) => {
    if (!selected.length) {
      message.info("请先选择题目");
      return;
    }
    const values = await batchForm.validateFields();
    await questionApi.batch({
      ids: selected.map(Number),
      action,
      ...values,
      tags: values.tags_text
        ? String(values.tags_text)
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean)
        : undefined,
    });
    message.success("批量操作完成");
    setBatchDifficultyOpen(false);
    setBatchTagsOpen(false);
    setSelected([]);
    batchForm.resetFields();
    load();
  };

  const remove = async (id: number) => {
    await questionApi.delete(id);
    message.success("已移入回收站");
    load();
  };

  const restore = async (id: number) => {
    await questionApi.restore(id);
    message.success("已恢复");
    load();
  };

  const hardDelete = async (id: number) => {
    await questionApi.hardDelete(id);
    message.success("题目已彻底删除");
    load();
  };

  const checkDuplicate = async () => {
    const values = await duplicateForm.validateFields();
    const data = await questionApi.duplicate(values);
    setDuplicates(data);
  };

  const uploadImage = async (file: File, field: "stem_image_url" | "analysis_image_url") => {
    const data = await questionApi.uploadImage(file);
    form.setFieldValue(field, data.url);
    form.setFieldValue("has_image", true);
    message.success("图片已上传");
    return false;
  };

  const subjectOptions = subjects.map((item) => ({ label: item.name, value: item.id }));
  const chapterOptions = chapters.map((item) => ({ label: `${item.subject_name || ""} / ${item.name}`, value: item.id }));
  const pointOptions = points.map((item) => ({ label: `${item.chapter_name || ""} / ${item.name}`, value: item.id }));

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>题目管理</Typography.Title>
          <Typography.Text type="secondary">筛选、编辑、发布、下架、删除和恢复题库题目。</Typography.Text>
        </div>
        <Button type="primary" icon={<Plus size={16} />} onClick={() => open()}>新增题目</Button>
      </div>
      <div className="panel">
        <Form layout="inline" className="filter-form">
          <Form.Item label="关键词">
            <Input
              allowClear
              prefix={<Search size={16} />}
              onPressEnter={(event) => setFilters((current) => ({ ...current, keyword: event.currentTarget.value, page: 1 }))}
            />
          </Form.Item>
          <Form.Item label="科目">
            <Select allowClear style={{ width: 170 }} options={subjectOptions} onChange={(value) => setFilters((current) => ({ ...current, subject_id: value, page: 1 }))} />
          </Form.Item>
          <Form.Item label="状态">
            <Select
              allowClear
              style={{ width: 140 }}
              options={[
                { label: "草稿", value: "draft" },
                { label: "待审核", value: "pending_review" },
                { label: "已发布", value: "published" },
                { label: "已下架", value: "offline" },
              ]}
              onChange={(value) => setFilters((current) => ({ ...current, status: value, page: 1 }))}
            />
          </Form.Item>
          <Form.Item label="回收站">
            <Switch onChange={(checked) => setFilters((current) => ({ ...current, include_deleted: checked, page: 1 }))} />
          </Form.Item>
          <Space wrap>
            <Button onClick={() => setDuplicateOpen(true)}>题干查重</Button>
            <Button onClick={() => batch("publish")}>批量发布</Button>
            <Button onClick={() => batch("offline")}>批量下架</Button>
            <Button onClick={() => setBatchDifficultyOpen(true)}>批量改难度</Button>
            <Button onClick={() => setBatchTagsOpen(true)}>批量打标签</Button>
            <Button danger onClick={() => batch("delete")}>批量删除</Button>
          </Space>
        </Form>
        <Table
          rowKey="id"
          rowSelection={{ selectedRowKeys: selected, onChange: setSelected }}
          dataSource={items}
          pagination={{ total, current: Number(filters.page), pageSize: Number(filters.page_size), onChange: (page, pageSize) => setFilters((current) => ({ ...current, page, page_size: pageSize })) }}
          columns={[
            { title: "题干", dataIndex: "stem", render: (value) => truncate(String(value), 72) },
            { title: "题型", dataIndex: "question_type", width: 100, render: (value) => questionTypeLabel[String(value)] || String(value) },
            { title: "科目/章节/知识点", width: 220, render: (_, row) => `${row.subject_name || "-"} / ${row.chapter_name || "-"} / ${row.knowledge_point_name || "-"}` },
            { title: "难度", dataIndex: "difficulty", width: 90, render: (value) => difficultyLabel[String(value)] || String(value) },
            { title: "状态", dataIndex: "status", width: 100, render: (value) => <Tag>{statusLabel[String(value)] || String(value)}</Tag> },
            { title: "正确率", dataIndex: "correct_rate", width: 90, render: (value) => `${value || 0}%` },
            { title: "更新时间", dataIndex: "updated_at", width: 130, render: (value) => shortDate(value) },
            {
              title: "操作",
              width: 180,
              render: (_, row) => (
                <Space>
                  <Button size="small" onClick={() => open(row)}>编辑</Button>
                  <Button size="small" danger onClick={() => remove(row.id)}>删除</Button>
                  <Button size="small" onClick={() => restore(row.id)}>恢复</Button>
                  <Button size="small" danger onClick={() => hardDelete(row.id)}>彻底删除</Button>
                </Space>
              ),
            },
          ]}
        />
      </div>

      <Modal title={editing === "new" ? "新增题目" : "编辑题目"} open={Boolean(editing)} onOk={save} onCancel={() => setEditing(null)} width={900}>
        <Form form={form} layout="vertical">
          <Form.Item label="题干" name="stem" rules={[{ required: true }]}>
            <Input.TextArea rows={4} />
          </Form.Item>
          <Space align="start" wrap>
            <Form.Item label="题型" name="question_type" rules={[{ required: true }]}>
              <Select style={{ width: 150 }} options={Object.entries(questionTypeLabel).map(([value, label]) => ({ value, label }))} />
            </Form.Item>
            <Form.Item label="正确答案" name="correct_answer" rules={[{ required: true }]}>
              <Input style={{ width: 150 }} placeholder="如 A 或 A,C" />
            </Form.Item>
            <Form.Item label="难度" name="difficulty">
              <Select style={{ width: 120 }} options={Object.entries(difficultyLabel).map(([value, label]) => ({ value, label }))} />
            </Form.Item>
            <Form.Item label="状态" name="status">
              <Select
                style={{ width: 130 }}
                options={[
                  { label: "草稿", value: "draft" },
                  { label: "待审核", value: "pending_review" },
                  { label: "已发布", value: "published" },
                  { label: "已下架", value: "offline" },
                ]}
              />
            </Form.Item>
          </Space>
          <Space align="start" wrap>
            <Form.Item label="科目" name="subject_id" rules={[{ required: true }]}>
              <Select style={{ width: 220 }} options={subjectOptions} />
            </Form.Item>
            <Form.Item label="章节" name="chapter_id" rules={[{ required: true }]}>
              <Select style={{ width: 260 }} options={chapterOptions} />
            </Form.Item>
            <Form.Item label="知识点" name="knowledge_point_id" rules={[{ required: true }]}>
              <Select style={{ width: 280 }} options={pointOptions} />
            </Form.Item>
          </Space>
          <Form.List name="options">
            {(fields, { add, remove }) => (
              <div className="option-editor">
                <div className="panel-title">选项</div>
                {fields.map((field) => (
                  <Space key={field.key} align="baseline" className="option-line">
                    <Form.Item {...field} name={[field.name, "option_key"]} rules={[{ required: true }]}>
                      <Input placeholder="A" style={{ width: 70 }} />
                    </Form.Item>
                    <Form.Item {...field} name={[field.name, "content"]} rules={[{ required: true }]}>
                      <Input placeholder="选项内容" style={{ width: 520 }} />
                    </Form.Item>
                    <Form.Item {...field} name={[field.name, "sort_order"]}>
                      <InputNumber min={0} style={{ width: 90 }} />
                    </Form.Item>
                    <Button danger onClick={() => remove(field.name)}>删除</Button>
                  </Space>
                ))}
                <Button onClick={() => add({ option_key: "", content: "", sort_order: fields.length + 1 })}>添加选项</Button>
              </div>
            )}
          </Form.List>
          <Form.Item label="解析" name="analysis" rules={[{ required: true }]}>
            <Input.TextArea rows={4} />
          </Form.Item>
          <Space align="start" wrap>
            <Form.Item label="来源" name="source">
              <Input style={{ width: 160 }} />
            </Form.Item>
            <Form.Item label="年份" name="year">
              <InputNumber min={1900} max={2100} />
            </Form.Item>
            <Form.Item label="学校/来源机构" name="school">
              <Input style={{ width: 220 }} />
            </Form.Item>
            <Form.Item label="标签，用英文逗号分隔" name="tags_text">
              <Input style={{ width: 260 }} />
            </Form.Item>
          </Space>
          <Space align="start" wrap>
            <Form.Item label="题干图片 URL" name="stem_image_url">
              <Input
                style={{ width: 360 }}
                addonAfter={
                  <Upload showUploadList={false} beforeUpload={(file) => uploadImage(file, "stem_image_url")}>
                    <Button type="link" size="small">上传</Button>
                  </Upload>
                }
              />
            </Form.Item>
            <Form.Item label="解析图片 URL" name="analysis_image_url">
              <Input
                style={{ width: 360 }}
                addonAfter={
                  <Upload showUploadList={false} beforeUpload={(file) => uploadImage(file, "analysis_image_url")}>
                    <Button type="link" size="small">上传</Button>
                  </Upload>
                }
              />
            </Form.Item>
          </Space>
        </Form>
      </Modal>

      <Modal title="题干查重" open={duplicateOpen} onOk={checkDuplicate} onCancel={() => setDuplicateOpen(false)} width={760} okText="开始查重">
        <Form form={duplicateForm} layout="vertical" initialValues={{ threshold: 0.82 }}>
          <Form.Item label="题干" name="stem" rules={[{ required: true }]}>
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item label="相似度阈值" name="threshold">
            <InputNumber min={0} max={1} step={0.01} />
          </Form.Item>
        </Form>
        <Table
          rowKey={(row) => String(row.question_id)}
          dataSource={duplicates}
          pagination={false}
          columns={[
            { title: "题目 ID", dataIndex: "question_id", width: 90 },
            { title: "相似度", dataIndex: "similarity", width: 100 },
            { title: "类型", dataIndex: "duplicate_type", width: 120 },
            { title: "题干", dataIndex: "stem", render: (value) => truncate(String(value), 80) },
          ]}
        />
      </Modal>

      <Modal title="批量修改难度" open={batchDifficultyOpen} onOk={() => batchWithValues("change_difficulty")} onCancel={() => setBatchDifficultyOpen(false)}>
        <Form form={batchForm} layout="vertical">
          <Form.Item label="难度" name="difficulty" rules={[{ required: true }]}>
            <Select options={Object.entries(difficultyLabel).map(([value, label]) => ({ value, label }))} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal title="批量打标签" open={batchTagsOpen} onOk={() => batchWithValues("tag")} onCancel={() => setBatchTagsOpen(false)}>
        <Form form={batchForm} layout="vertical">
          <Form.Item label="标签，用英文逗号分隔" name="tags_text" rules={[{ required: true }]}>
            <Input placeholder="例如：重点,易错,循环系统" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}