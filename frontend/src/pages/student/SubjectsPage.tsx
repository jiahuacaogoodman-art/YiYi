import { Button, Col, Collapse, Empty, Progress, Row, Space, Tag, Typography } from "antd";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BookMarked, ChevronDown, ChevronRight, Layers3 } from "lucide-react";
import { taxonomyApi } from "../../api/client";
import type { Chapter, KnowledgePoint, Subject } from "../../types/domain";
import { compactNumber, percent } from "../../utils/format";

export function SubjectsPage() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [chapters, setChapters] = useState<Record<number, Chapter[]>>({});
  const [points, setPoints] = useState<Record<number, KnowledgePoint[]>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    taxonomyApi.subjects({ enabled: true, page_size: 100 }).then((data) => {
      setSubjects(data.items);
      setLoading(false);
    });
  }, []);

  const loadChapters = async (subjectId: number) => {
    if (chapters[subjectId]) return;
    const data = await taxonomyApi.chapters({ subject_id: subjectId, enabled: true, page_size: 200 });
    setChapters((current) => ({ ...current, [subjectId]: data.items }));
  };

  const loadPoints = async (chapterId: number) => {
    if (points[chapterId]) return;
    const data = await taxonomyApi.knowledgePoints({ chapter_id: chapterId, enabled: true, page_size: 200 });
    setPoints((current) => ({ ...current, [chapterId]: data.items }));
  };

  return (
    <div className="page">
      <section className="library-hero">
        <div>
          <span>毅医题库</span>
          <Typography.Title level={1}>按学科定位，按章节推进</Typography.Title>
          <Typography.Text>每个科目都可以继续展开到章节和知识点，适合期末复习、阶段训练和考前冲刺。</Typography.Text>
        </div>
        <div className="library-hero__meta">
          <strong>{compactNumber(subjects.reduce((total, item) => total + Number(item.question_count || 0), 0))}</strong>
          <span>题库总量</span>
        </div>
      </section>
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>题库选择</Typography.Title>
          <Typography.Text type="secondary">按医学学科、章节和知识点选择练习入口。</Typography.Text>
        </div>
        <Link to="/practice">
          <Button type="primary" icon={<Layers3 size={16} />}>自主组题</Button>
        </Link>
      </div>
      {subjects.length ? (
        <Row gutter={[16, 16]}>
          {subjects.map((subject) => (
            <Col xs={24} lg={12} xl={8} key={subject.id}>
              <div className="subject-panel">
                <div className="subject-panel__head">
                  <span className="subject-icon"><BookMarked size={20} /></span>
                  <div>
                    <Typography.Title level={4}>{subject.name}</Typography.Title>
                    <Typography.Text type="secondary">{subject.description || subject.code}</Typography.Text>
                  </div>
                </div>
                <div className="subject-panel__stats">
                  <span>{compactNumber(subject.question_count)} 题</span>
                  <span>已刷 {compactNumber(subject.practiced_count)}</span>
                  <span>{percent(subject.correct_rate)}</span>
                </div>
                <Progress percent={subject.correct_rate} size="small" />
                <Space wrap className="subject-panel__actions">
                  <Link to={`/practice?subject_id=${subject.id}`}>
                    <Button type="primary">科目练习</Button>
                  </Link>
                  <Button onClick={() => loadChapters(subject.id)} icon={chapters[subject.id] ? <ChevronDown size={16} /> : <ChevronRight size={16} />}>查看章节</Button>
                </Space>
                {chapters[subject.id] ? (
                  <Collapse
                    ghost
                    className="compact-collapse"
                    onChange={(keys) => keys.forEach((key) => loadPoints(Number(key)))}
                    items={chapters[subject.id].map((chapter) => ({
                      key: chapter.id,
                      label: (
                        <span className="chapter-label">
                          {chapter.name}
                          <Tag>{chapter.question_count} 题</Tag>
                        </span>
                      ),
                      children: (
                        <Space direction="vertical" className="full-width">
                          <Link to={`/practice?subject_id=${subject.id}&chapter_id=${chapter.id}`}>练习本章</Link>
                          {(points[chapter.id] || []).map((point) => (
                            <Link key={point.id} to={`/practice?subject_id=${subject.id}&chapter_id=${chapter.id}&knowledge_point_id=${point.id}`}>
                              {point.name} <Tag>{point.question_count} 题</Tag>
                            </Link>
                          ))}
                        </Space>
                      ),
                    }))}
                  />
                ) : null}
              </div>
            </Col>
          ))}
        </Row>
      ) : (
        <div className="panel">
          <Empty description={loading ? "正在加载科目" : "暂无启用科目"} />
        </div>
      )}
    </div>
  );
}