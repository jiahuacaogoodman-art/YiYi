import { Button, Card, Empty, Form, Select, Space, Typography, message } from "antd";
import { useEffect, useState } from "react";
import { Heart } from "lucide-react";
import { practiceApi, questionApi, taxonomyApi } from "../../api/client";
import { QuestionViewer } from "../../components/QuestionViewer";
import type { Chapter, Question, Subject } from "../../types/domain";

export function FavoritesPage() {
  const [items, setItems] = useState<Question[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [filters, setFilters] = useState<Record<string, unknown>>({});

  const load = () => practiceApi.favorites({ page_size: 100, ...filters }).then((data) => setItems(data.items));

  useEffect(() => {
    taxonomyApi.subjects({ page_size: 100 }).then((data) => setSubjects(data.items));
  }, []);

  useEffect(() => {
    load();
  }, [filters]);

  const unfavorite = async (id: number) => {
    await questionApi.unfavorite(id);
    message.success("已取消收藏");
    load();
  };

  return (
    <div className="page">
      <div className="page-heading page-heading--hero">
        <div>
          <span className="page-heading__eyebrow">重点收藏</span>
          <Typography.Title level={2}>收藏题</Typography.Title>
          <Typography.Text type="secondary">集中复习已收藏题目，支持按科目、章节和难度筛选。</Typography.Text>
        </div>
        <span className="page-heading__badge"><Heart size={18} /> {items.length} 道收藏</span>
      </div>
      <div className="panel">
        <Form layout="inline" className="filter-form">
          <Form.Item label="科目">
            <Select
              allowClear
              style={{ width: 180 }}
              options={subjects.map((item) => ({ label: item.name, value: item.id }))}
              onChange={async (value) => {
                setFilters((current) => ({ ...current, subject_id: value, chapter_id: undefined }));
                setChapters(value ? (await taxonomyApi.chapters({ subject_id: value, page_size: 200 })).items : []);
              }}
            />
          </Form.Item>
          <Form.Item label="章节">
            <Select
              allowClear
              style={{ width: 180 }}
              options={chapters.map((item) => ({ label: item.name, value: item.id }))}
              onChange={(value) => setFilters((current) => ({ ...current, chapter_id: value }))}
            />
          </Form.Item>
          <Form.Item label="难度">
            <Select
              allowClear
              style={{ width: 140 }}
              options={[
                { label: "简单", value: "easy" },
                { label: "中等", value: "medium" },
                { label: "困难", value: "hard" },
              ]}
              onChange={(value) => setFilters((current) => ({ ...current, difficulty: value }))}
            />
          </Form.Item>
        </Form>
      </div>
      <Space direction="vertical" size={16} className="full-width section-row">
        {items.length ? (
          items.map((item) => (
            <Card key={item.id} variant="borderless">
              <div className="list-card-head">
                <span />
                <Button danger onClick={() => unfavorite(item.id)}>取消收藏</Button>
              </div>
              <QuestionViewer question={item} submitted />
            </Card>
          ))
        ) : (
          <div className="panel">
            <Empty description="暂无收藏题，做题时可以把重点题加入收藏" />
          </div>
        )}
      </Space>
    </div>
  );
}