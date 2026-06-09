import { Button, Col, Empty, Progress, Row, Space, Tag, Typography } from "antd";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart3, BookOpen, ChevronDown, ClipboardList, Heart, History, MessageSquare, NotebookPen, PlayCircle, ThumbsUp } from "lucide-react";
import { statisticsApi, taxonomyApi } from "../../api/client";
import { BrandMark } from "../../components/BrandMark";
import { EChart } from "../../components/EChart";
import type { Subject, UserStatistics } from "../../types/domain";
import { barOption, lineOption } from "../../utils/charts";
import { compactNumber, percent } from "../../utils/format";

const studyTabs = ["全部科目", "待继续", "已完成", "未开始"];

export function HomePage() {
  const [stats, setStats] = useState<UserStatistics | null>(null);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeStudyTab, setActiveStudyTab] = useState(studyTabs[0]);

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

  const visibleSubjects = useMemo(() => {
    if (activeStudyTab === "待继续") {
      return subjects.filter((subject) => subject.practiced_count > 0 && subject.practiced_count < subject.question_count);
    }
    if (activeStudyTab === "已完成") {
      return subjects.filter((subject) => subject.question_count > 0 && subject.practiced_count >= subject.question_count);
    }
    if (activeStudyTab === "未开始") {
      return subjects.filter((subject) => subject.practiced_count === 0);
    }
    return subjects;
  }, [activeStudyTab, subjects]);

  const quickItems = [
    { to: "/subjects", title: "主观题", hint: "按学科进入", icon: <BookOpen size={22} /> },
    { to: "/practice", title: "自主组题", hint: "自由选择模式", icon: <NotebookPen size={22} /> },
    { to: "/practice?mode=wrong", title: "错题重刷", hint: `${compactNumber(stats?.wrong_count)} 道待复盘`, icon: <History size={22} /> },
    { to: "/exams", title: "模拟考试", hint: "限时测评", icon: <ClipboardList size={22} /> },
  ];

  const toolItems = [
    { to: "/wrong", title: "错题", icon: <History size={22} /> },
    { to: "/favorites", title: "收藏", icon: <Heart size={22} /> },
    { to: "/notes", title: "笔记", icon: <NotebookPen size={22} /> },
    { to: "/comments", title: "评论", icon: <MessageSquare size={22} /> },
    { to: "/likes", title: "点赞", icon: <ThumbsUp size={22} /> },
  ];

  return (
    <div className="page">
      <section className="hero-dashboard">
        <div className="hero-dashboard__content">
          <span className="hero-dashboard__eyebrow">今日题库 · 医学训练工作台</span>
          <Typography.Title level={1}>稳稳刷完今天这一轮</Typography.Title>
          <Typography.Paragraph>
            题库按科目、章节和知识点组织，错题、收藏、模拟考试自动沉淀成复习路径。
          </Typography.Paragraph>
          <div className="hero-dashboard__actions">
            <Link to="/practice">
              <Button type="primary" size="large" icon={<PlayCircle size={18} />}>开始刷题</Button>
            </Link>
            <Link to="/subjects">
              <Button size="large" icon={<BookOpen size={18} />}>进入题库</Button>
            </Link>
          </div>
        </div>
        <div className="hero-dashboard__visual">
          <div className="hero-dashboard__plate">
            <BrandMark size="large" />
          </div>
          <div className="hero-dashboard__mini">
            <span>{compactNumber(stats?.total_answers)} 题</span>
            <span>{percent(stats?.correct_rate)}</span>
            <span>{compactNumber(stats?.wrong_count)} 错题</span>
          </div>
        </div>
      </section>

      <div className="quick-grid">
        {quickItems.map((item) => (
          <Link className="quick-card" to={item.to} key={item.title}>
            <span className="quick-card__icon">{item.icon}</span>
            <span className="quick-card__title">{item.title}</span>
            <span className="quick-card__hint">{item.hint}</span>
          </Link>
        ))}
      </div>

      <Row gutter={[16, 16]} className="section-row">
        <Col xs={24} xl={13}>
          <div className="panel today-card">
            <div className="today-card__head">
              <div>
                <Typography.Title level={3}>今日统计</Typography.Title>
                <Typography.Text type="secondary">更新时间：{new Date().toLocaleTimeString("zh-CN", { hour12: false })}</Typography.Text>
              </div>
              <BarChart3 size={22} />
            </div>
            <div className="today-card__stats">
              <div>
                <strong>{compactNumber(todayCount)}</strong>
                <span>今日做题</span>
              </div>
              <div>
                <strong>{compactNumber(stats?.total_answers)}</strong>
                <span>累计题量</span>
              </div>
              <div>
                <strong>{percent(stats?.correct_rate)}</strong>
                <span>总正确率</span>
              </div>
              <div>
                <strong>{compactNumber(stats?.wrong_count)}</strong>
                <span>错题待刷</span>
              </div>
            </div>
          </div>
        </Col>
        <Col xs={24} xl={11}>
          <div className="panel tool-strip">
            {toolItems.map((item) => (
              <Link className="tool-strip__item" to={item.to} key={item.title}>
                <span className="tool-strip__icon">{item.icon}</span>
                <span>{item.title}</span>
              </Link>
            ))}
          </div>
        </Col>
      </Row>

      <Row gutter={[16, 16]} className="section-row">
        <Col xs={24} xl={13}>
          <div className="panel study-board">
            <div className="study-board__tabs">
              {studyTabs.map((item) => (
                <button
                  type="button"
                  key={item}
                  className={item === activeStudyTab ? "study-board__tab study-board__tab--active" : "study-board__tab"}
                  onClick={() => setActiveStudyTab(item)}
                >
                  {item}
                </button>
              ))}
            </div>
            {visibleSubjects.length ? (
              <div className="subject-list">
                {visibleSubjects.map((subject) => (
                  <div className="subject-list__row" key={subject.id}>
                    <span className="subject-list__toggle"><ChevronDown size={18} /></span>
                    <div>
                      <div className="subject-list__title">{subject.name}</div>
                      <div className="subject-list__meta">
                        {compactNumber(subject.practiced_count)} / {compactNumber(subject.question_count)} 已完成
                      </div>
                    </div>
                    <div className="subject-list__progress">
                      <span>{compactNumber(subject.practiced_count)}/{compactNumber(subject.question_count)}</span>
                      <Progress percent={subject.question_count ? Math.round(subject.correct_rate || 0) : 0} showInfo={false} size="small" />
                    </div>
                    <Link to={`/practice?subject_id=${subject.id}`}>
                      <Button type="text">继续做</Button>
                    </Link>
                  </div>
                ))}
              </div>
            ) : (
              <Empty description={loading ? "正在加载科目" : "当前筛选下暂无科目"} />
            )}
          </div>
        </Col>
        <Col xs={24} xl={11}>
          <div className="panel">
            {stats?.recent_7_days?.length ? <EChart option={trend} /> : <Empty description="暂无刷题趋势" />}
          </div>
          <div className="panel section-row">
            {stats?.subject_accuracy?.length ? <EChart option={subjectChart} /> : <Empty description="暂无科目正确率" />}
          </div>
          <div className="panel section-row">
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