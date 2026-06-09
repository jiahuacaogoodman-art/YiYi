import { Button, Col, Empty, Row, Space, Table, Tag, Typography } from "antd";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart3, BookOpen, ClipboardList, Heart, History, PlayCircle } from "lucide-react";
import { statisticsApi, taxonomyApi } from "../../api/client";
import { EChart } from "../../components/EChart";
import { MetricCard } from "../../components/MetricCard";
import type { Subject, UserStatistics } from "../../types/domain";
import { barOption, lineOption } from "../../utils/charts";
import { compactNumber, percent } from "../../utils/format";

export function HomePage() {
  const [stats, setStats] = useState<UserStatistics | null>(null);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([statisticsApi.user(), taxonomyApi.subjects({ enabled: true, page_size: 12 })])
      .then(([statData, subjectData]) => {
        setStats(statData);
        setSubjects(subjectData.items);
      })
      .finally(() => setLoading(false));
  }, []);

  const trend = useMemo(() => {
    const rows = stats?.recent_7_days || [];
    return lineOption(
      "最近 7 天刷题趋势",
      rows.map((row) => String(row.date || "")),
      rows.map((row) => Number(row.total || row.count || 0)),
    );
  }, [stats]);

  const subjectChart = useMemo(() => {
    const rows = stats?.subject_accuracy || [];
    return barOption(
      "各科正确率",
      rows.map((row) => String(row.subject_name || "")),
      rows.map((row) => Number(row.correct_rate || 0)),
    );
  }, [stats]);

  const todayCount = useMemo(() => {
    const today = new Date().toISOString().slice(0, 10);
    const row = (stats?.recent_7_days || []).find((item) => String(item.date || "").slice(0, 10) === today);
    return Number(row?.total || row?.count || 0);
  }, [stats]);

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>学习首页</Typography.Title>
          <Typography.Text type="secondary">从进度、错题和推荐章节开始今天的复习。</Typography.Text>
        </div>
        <Space wrap>
          <Link to="/practice">
            <Button type="primary" icon={<PlayCircle size={16} />}>开始刷题</Button>
          </Link>
          <Link to="/wrong">
            <Button icon={<History size={16} />}>错题本</Button>
          </Link>
          <Link to="/favorites">
            <Button icon={<Heart size={16} />}>收藏题</Button>
          </Link>
          <Link to="/exams">
            <Button icon={<ClipboardList size={16} />}>模拟考试</Button>
          </Link>
        </Space>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard label="总刷题数" value={compactNumber(stats?.total_answers)} hint="累计提交答案" icon={<BookOpen size={18} />} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard label="正确率" value={percent(stats?.correct_rate)} hint={`${compactNumber(stats?.correct_count)} 道正确`} icon={<BarChart3 size={18} />} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard label="今日刷题" value={compactNumber(todayCount)} hint="来自最近 7 天趋势" icon={<History size={18} />} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard label="错题数量" value={compactNumber(stats?.wrong_count)} hint="建议优先重刷" icon={<Heart size={18} />} />
        </Col>
      </Row>

      <Row gutter={[16, 16]} className="section-row">
        <Col xs={24} xl={14}>
          <div className="panel">
            {stats?.recent_7_days?.length ? <EChart option={trend} /> : <Empty description="暂无刷题趋势" />}
          </div>
        </Col>
        <Col xs={24} xl={10}>
          <div className="panel">
            {stats?.subject_accuracy?.length ? <EChart option={subjectChart} /> : <Empty description="暂无科目正确率" />}
          </div>
        </Col>
      </Row>

      <Row gutter={[16, 16]} className="section-row">
        <Col xs={24} xl={14}>
          <div className="panel">
            <div className="panel-title">推荐继续学习</div>
            <Table
              rowKey="id"
              loading={loading}
              dataSource={subjects}
              pagination={false}
              columns={[
                { title: "科目", dataIndex: "name" },
                { title: "题量", dataIndex: "question_count", width: 90 },
                { title: "已刷", dataIndex: "practiced_count", width: 90 },
                { title: "正确率", dataIndex: "correct_rate", width: 100, render: (value) => percent(value) },
                {
                  title: "操作",
                  width: 120,
                  render: (_, row) => <Link to={`/practice?subject_id=${row.id}`}>开始练习</Link>,
                },
              ]}
            />
          </div>
        </Col>
        <Col xs={24} xl={10}>
          <div className="panel">
            <div className="panel-title">推荐复习章节</div>
            <Space direction="vertical" className="full-width">
              {(stats?.recommended_chapters || []).length ? (
                stats?.recommended_chapters.map((row) => (
                  <div key={String(row.chapter_id)} className="list-row">
                    <span>{String(row.chapter_name || "-")}</span>
                    <Tag color="gold">掌握度 {percent(Number(row.mastery || 0))}</Tag>
                  </div>
                ))
              ) : (
                <Empty description="暂无推荐章节" />
              )}
            </Space>
          </div>
        </Col>
      </Row>
    </div>
  );
}