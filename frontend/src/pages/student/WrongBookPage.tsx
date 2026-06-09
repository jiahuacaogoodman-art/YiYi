import { Button, Card, Empty, Form, Select, Space, Tag, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { practiceApi, taxonomyApi } from "../../api/client";
import { QuestionViewer } from "../../components/QuestionViewer";
import type { Chapter, KnowledgePoint, Subject, WrongQuestion } from "../../types/domain";
import { shortDate } from "../../utils/format";

export function WrongBookPage() {
  const [items, setItems] = useState<WrongQuestion[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [points, setPoints] = useState<KnowledgePoint[]>([]);
  const [filters, setFilters] = useState<Record<string, unknown>>({ sort: "recent" });

  const load = () => practiceApi.wrong({ page_size: 100, ...filters }).then((data) => setItems(data.items));

  useEffect(() => {
    taxonomyApi.subjects({ page_size: 100 }).then((data) => setSubjects(data.items));
  }, []);

  useEffect(() => {
    load();
  }, [filters]);

  const remove = async (questionId: number) => {
    await practiceApi.removeWrong(questionId);
    message.success("已移出错题本");
    load();
  };

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>错题本</Typography.Title>
          <Typography.Text type="secondary">按科目、章节和错误次数筛选复习。</Typography.Text>
        </div>
        <Link to="/practice?mode=wrong">
          <Button type="primary">错题重刷</Button>
        </Link>
      </div>
      <div className="panel">
        <Form layout="inline" className="filter-form">
          <Form.Item label="科目">
            <Select
              allowClear
              style={{ width: 180 }}
              options={subjects.map((item) => ({ label: item.name, value: item.id }))}
              onChange={async (value) => {
                setFilters((current) => ({ ...current, subject_id: value, chapter_id: undefined, knowledge_point_id: undefined }));
                setChapters(value ? (await taxonomyApi.chapters({ subject_id: value, page_size: 200 })).items : []);
                setPoints([]);
              }}
            />
          </Form.Item>
          <Form.Item label="章节">
            <Select
              allowClear
              style={{ width: 180 }}
              options={chapters.map((item) => ({ label: item.name, value: item.id }))}
              onChange={async (value) => {
                setFilters((current) => ({ ...current, chapter_id: value, knowledge_point_id: undefined }));
                setPoints(value ? (await taxonomyApi.knowledgePoints({ chapter_id: value, page_size: 200 })).items : []);
              }}
            />
          </Form.Item>
          <Form.Item label="知识点">
            <Select
              allowClear
              style={{ width: 200 }}
              options={points.map((item) => ({ label: item.name, value: item.id }))}
              onChange={(value) => setFilters((current) => ({ ...current, knowledge_point_id: value }))}
            />
          </Form.Item>
          <Form.Item label="排序">
            <Select
              value={String(filters.sort)}
              style={{ width: 160 }}
              options={[
                { label: "最近错误", value: "recent" },
                { label: "错误次数", value: "wrong_count" },
              ]}
              onChange={(value) => setFilters((current) => ({ ...current, sort: value }))}
            />
          </Form.Item>
        </Form>
      </div>
      <Space direction="vertical" size={16} className="full-width section-row">
        {items.length ? (
          items.map((item) => (
            <Card key={item.id} variant="borderless">
              <div className="list-card-head">
                <Space wrap>
                  <Tag color="red">错 {item.wrong_count} 次</Tag>
                  <Tag>{shortDate(item.last_wrong_at)}</Tag>
                </Space>
                <Button danger onClick={() => remove(item.question.id)}>移出错题本</Button>
              </div>
              <QuestionViewer question={item.question} submitted />
            </Card>
          ))
        ) : (
          <div className="panel">
            <Empty description="暂无错题" />
          </div>
        )}
      </Space>
    </div>
  );
}